service ImagingServer{
  bool ping(),
  string identify(),
  string stream_url(),
  oneway void shutdown(),
  oneway void start_capture(1:string data_code),
  binary retrieve_still_png(1:string with_data_code),
  binary retrieve_still_jpg(1:string with_data_code),
  map<string, list<string>> enumerate_methods()
}
