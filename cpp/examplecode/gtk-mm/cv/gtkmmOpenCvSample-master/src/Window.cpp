#include "Window.h"

Window::Window(){
	cam.open(0);

	set_default_size(1920, 1080);

	cam.set(CV_CAP_PROP_FRAME_WIDTH, 1920);
	cam.set(CV_CAP_PROP_FRAME_HEIGHT, 1080);
	




    add(this->scrolledWindow);
    scrolledWindow.add(this->fixed);
    
    fixed.add(this->panel1);
    fixed.move(this->panel1, 10, 10);
    panel1.set_size_request(505, 460);
    panel1.set_shadow_type(Gtk::SHADOW_IN);
    
    fixed.add(this->panel2);
    fixed.move(this->panel2, 525, 10);
    panel2.set_size_request(105, 460);
    panel2.set_shadow_type(Gtk::SHADOW_ETCHED_IN);

    this->set_title("Panel example");
    this->resize(640, 480);





  // put the box into the main window.
  panel1.add(m_box1);
  panel2.add(m_box2);
  m_box1.pack_start(camDrawer);


  m_button1.signal_clicked().connect(sigc::bind<Glib::ustring>(
              sigc::mem_fun(*this, &Window::on_button_clicked), "button 1"));
  m_box2.pack_start(m_button1);

  m_button2.signal_clicked().connect(sigc::bind<-1, Glib::ustring>(
              sigc::mem_fun(*this, &Window::on_button_clicked), "button 2"));
  m_box2.pack_start(m_button2);





	show_all();

	//listen for camera in thread
	camThread = std::thread([&]{
		cv::Mat m;
		camClose = false;
		while(cam.isOpened() && !camClose){
			if(cam.read(m)){
				camMutex.lock();
				camMatThread = m.clone();
				camMutex.unlock();
				signalCamFrame.emit();
			}
		}
	});

	//copy camera mat in thread
	signalCamFrame.connect([&]{
		camMutex.lock();
		camMat = camMatThread.clone();
		camMutex.unlock();

		camDrawer.setCvMat(camMat);
	});


}

Window::~Window(){
	camClose = true;
	if(camThread.joinable())
		camThread.join();
	cam.release();
}


void Window::on_button_clicked(Glib::ustring data)
{
  std::cout << "Hello World - " << data << " was pressed" << std::endl;
}

