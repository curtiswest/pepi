exception ImageUnavailable {
    1: string message,
}

service ImagingServer{
  bool ping(),
  string identify(),
  list<string> stream_urls(),
  oneway void shutdown(),
  oneway void start_capture(1:string data_code),
  list<string> retrieve_still_pngs(1:string with_data_code) throws(1:ImageUnavailable unavailable),
  list<string> retrieve_still_jpgs(1:string with_data_code) throws(1:ImageUnavailable unavailable),
  map<string, list<string>> enumerate_methods()
}
