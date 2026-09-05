#ifndef WINDOW_H
#define WINDOW_H

#include "CvDrawer.h"
#include "gtkmm.h"
#include <opencv2/opencv.hpp>
#include <thread>
#include <atomic>
#include <gtkmm/box.h>

class Window: public Gtk::Window{
public:
    Window();
	~Window();

	cv::VideoCapture cam;
	cv::Mat camMatThread;
	cv::Mat camMat;
	CvDrawer camDrawer;
	std::thread camThread;
	std::mutex camMutex;
	std::atomic_bool camClose;

	Glib::Dispatcher signalCamFrame;


protected:
  void on_button_clicked(Glib::ustring data);



  Gtk::Fixed fixed;
  Gtk::ScrolledWindow scrolledWindow;
  Gtk::Frame panel1;
  Gtk::Frame panel2;


  Gtk::Box m_box1;
  Gtk::VBox m_box2;
  Gtk::Button m_button1, m_button2;


};

#endif // WINDOW_H
