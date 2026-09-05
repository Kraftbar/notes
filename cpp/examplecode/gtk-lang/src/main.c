#include <gtk/gtk.h>

void putText(GtkTextBuffer *buffer){
    gtk_text_buffer_set_text (buffer, "Hello, this is some text", -1);
    
}


int main(int argc, char *argv[])
{
    GtkBuilder      *builder; 
    GtkWidget       *window;

    GtkWidget       *view;
    GtkTextBuffer *buffer;

    gtk_init(&argc, &argv);

    builder = gtk_builder_new();
    gtk_builder_add_from_file (builder, "glade/window_main.glade", NULL);

    window = GTK_WIDGET(gtk_builder_get_object(builder, "window_main"));

    view = GTK_WIDGET(gtk_builder_get_object(builder, "texttest"));
    buffer = gtk_text_view_get_buffer (GTK_TEXT_VIEW (view));

    putText(buffer);
    
    gtk_builder_connect_signals(builder, NULL);

    g_object_unref(builder);

    gtk_widget_show(window);                
    gtk_main();

    return 0;
}

void on_btn_print_txt_clicked(GtkButton *button, GtkLabel *text_label)
{
  printf("asdasd \n");
}

void tessst(GtkButton *button, GtkLabel *text_label)
{
  printf("asdasd \n");
}

// called when window is closed
void on_window_main_destroy()
{
    gtk_main_quit();
}
