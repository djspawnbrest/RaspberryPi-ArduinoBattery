#include <lxpanel/plugin.h>

#include <linux/i2c-dev.h>
#include <gtk/gtk.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <time.h>
#include <glib.h>
#include <glib/gi18n.h>
#include <string.h>

typedef struct 
{
  char *delay_in_ms_str;
  int delay_in_ms;
  unsigned int timer;
  GtkWidget *prg;
  GtkWidget *vbox;
  GtkWidget *main;
  GtkWidget *label;
} ArdBattApp;

  // Arduino Vref (measure)
  const float VRef = 1.082;
  // IN <-[ Rh ]--(analogInPin)--[ Rl ]--|GND
  const float Rh = 46.87; // kOm
  const float Rl = 10.11; // kOm
  const float cell_min = 3.20; // min charge cell
  const float cell_max = 4.10; // max charge cell
  int AnalogVal;
  float VoltMult;
  float Volt;
  int Percent;
  int fd;
	char *fileName = "/dev/i2c-1";
	int  address = 0x20;
  int flag20 = 1;
  int status;

static int update_display(ArdBattApp *pArdBatt) {
  
  unsigned char buf[3];
	read(fd, buf, 3);
	VoltMult = (Rh + Rl) / Rl;
	AnalogVal = buf[0] << 8 | buf[1];
	Volt = AnalogVal * VoltMult * VRef / 1023;
	Percent = ((Volt - cell_min) * 100) / (cell_max - cell_min);
	if (Percent < 0) {
		Percent = 0;
	} else if (Percent > 100) {
		Percent = 100;
	}
  
  char *chg = "";
  
  if ( buf[2] ) {
    chg = "CHG";
  }
  
  double fraction = Percent/100.00;
  char prgBuf[5] = {'\0'};
  snprintf(prgBuf, sizeof(prgBuf), "%d%%", Percent);
  gtk_progress_bar_set_text(GTK_PROGRESS_BAR(pArdBatt->prg), prgBuf);
  gtk_progress_bar_set_fraction (GTK_PROGRESS_BAR(pArdBatt->prg), fraction);

  // make a label out of the ID
  char labBuf[25] = {'\0'};
  snprintf(labBuf, sizeof(labBuf), "%.2fV %s", Volt, chg);
  gtk_label_set_markup(GTK_LABEL(pArdBatt->label), labBuf);
  
  if (Percent < 20){
    if (flag20 == 1) {
      flag20 = 0;
      system("zenity --warning --title='Battery low level WARNING' --width=100 --height=100 --no-wrap --text='<big><b>Battery level is too low:</b></big>\n\nBattery level less than 20%!\nPlease <b>CONNECT</b> the charger or your system will be shuted down soon!'");
    }
  }
  
  if (Percent > 28) {
    flag20 = 1;
  }
  
  return 1;
}

static void set_delay_in_ms_str(ArdBattApp *pArdBatt) {
  free(pArdBatt->delay_in_ms_str);
  pArdBatt->delay_in_ms_str = malloc(8);
  snprintf(pArdBatt->delay_in_ms_str, 8, "%d", pArdBatt->delay_in_ms);
}

static void update_timer(ArdBattApp *pArdBatt) {
  if (pArdBatt->delay_in_ms_str != NULL)
    pArdBatt->delay_in_ms = atoi(pArdBatt->delay_in_ms_str);
  if (pArdBatt->timer != 0) {
    g_source_remove(pArdBatt->timer);
  }
  if (pArdBatt->delay_in_ms <= 10) {
    pArdBatt->delay_in_ms = 1000;
    set_delay_in_ms_str(pArdBatt);
  }
  if (pArdBatt->delay_in_ms > 2000 || pArdBatt->delay_in_ms % 1000 == 0)
    pArdBatt->timer = g_timeout_add_seconds(pArdBatt->delay_in_ms / 1000, 
                                      (GSourceFunc) update_display,
                                      (gpointer) pArdBatt);
  else
    pArdBatt->timer= g_timeout_add(pArdBatt->delay_in_ms, 
                    (GSourceFunc) update_display, (gpointer) pArdBatt);
}

GtkWidget *test_constructor(LXPanel *panel, config_setting_t *settings)
{
  (void)panel;
  (void)settings;
 
  ArdBattApp *pArdBatt = g_new0(ArdBattApp, 1);
 
  if (pArdBatt->delay_in_ms == 0)
    pArdBatt->delay_in_ms = 1000;
  set_delay_in_ms_str(pArdBatt);
  
  fd = open(fileName, O_RDWR);
  ioctl(fd, I2C_SLAVE, address);
  
  //---------------------- STYLES ----------------------------
  PangoFontDescription *prbr;
  prbr = pango_font_description_new();
  pango_font_description_set_family(prbr, "Arial");
  pango_font_description_set_size(prbr, 7 * PANGO_SCALE);
  PangoAttrList *attrlist;
  PangoAttribute *attr;
  PangoFontDescription *df;
  attrlist = pango_attr_list_new();
  df = pango_font_description_new();
  pango_font_description_set_family(df, "Arial");
  pango_font_description_set_size(df, 5/*<-fontsize*/ * PANGO_SCALE);
  attr = pango_attr_font_desc_new(df);
  pango_font_description_free(df);
  pango_attr_list_insert(attrlist, attr);
  gtk_label_set_attributes(GTK_LABEL(pArdBatt->label), attrlist);
  gtk_label_set_justify(GTK_LABEL(pArdBatt->label), GTK_JUSTIFY_CENTER);
  gtk_widget_set_size_request(GTK_WIDGET(pArdBatt->label), -1, -1);
  GtkRequisition size;
  gtk_widget_set_size_request(GTK_WIDGET(pArdBatt->label), size.width, -1);
  //---------------------------------------------------------

  pArdBatt->label = gtk_label_new("");
  gtk_widget_show(pArdBatt->label);
 
  pArdBatt->vbox = gtk_vbox_new (FALSE, 2);
  gtk_container_set_border_width (GTK_CONTAINER(pArdBatt->vbox), 2);
  gtk_widget_set_size_request(pArdBatt->vbox, -1, 25);
  gtk_widget_show(pArdBatt->vbox);
 
  pArdBatt->prg = gtk_progress_bar_new();
  gtk_widget_modify_font(pArdBatt->prg, prbr);
  gtk_widget_set_size_request(pArdBatt->prg, -1, 12);
  gtk_progress_bar_pulse (GTK_PROGRESS_BAR (pArdBatt->prg));
  gtk_widget_show(pArdBatt->prg);

  pArdBatt->main = gtk_event_box_new();

  gtk_widget_set_has_window(pArdBatt->main, FALSE);

  lxpanel_plugin_set_data(pArdBatt->main, pArdBatt, g_free);

  gtk_container_set_border_width(GTK_CONTAINER(pArdBatt->main), 2);

  gtk_container_add(GTK_CONTAINER (pArdBatt->main), pArdBatt->vbox);
  gtk_box_pack_start(GTK_BOX(pArdBatt->vbox), pArdBatt->prg, TRUE, FALSE, 0);
  gtk_box_pack_end(GTK_BOX(pArdBatt->vbox), pArdBatt->label, TRUE, TRUE, 0);

  gtk_widget_set_size_request(pArdBatt->main, 80, -1);

  // updates
  update_display(pArdBatt);

  update_timer(pArdBatt);
 
  return pArdBatt->main;
}

FM_DEFINE_MODULE(lxpanel_gtk, test)

/* Plugin descriptor. */
LXPanelPluginInit fm_module_init_lxpanel_gtk = {
  .name = "Arduino Battery by Spawn",
  .description = "Arduino Battery indicator by Spawn",
  .new_instance = test_constructor,
};
