/*******************************************************************************
 * File: pepi.thrift
 * Author: Curtis West
 * -----------------------------
 * Interface definition file for Apache Thrift.
 ******************************************************************************/

/*******************************************************************************
Thrown when a requested image is not available on the server
*******************************************************************************/
exception ImageUnavailable {
    1: string message,
}

/*******************************************************************************
A Camera provides images from a physical camera in the form of RGB arrays.
*******************************************************************************/
service Camera {
  /* still
   * description: returns a still image capture from the camera at the currently
   *              set resolution
   * returns: multidimensional array of row, column, RGB representing the image
   */
   list<list<list<i16>>> still()

  /* low_res_still
   * description: gets a 640 x 480px still from this camera for previewing
   * returns: multidimensional array of row, column, RGB representing the image
   */
   list<list<list<i16>>> low_res_still()

  /* still
   * description: gets the maximum resolution supported by this camera
   * returns: a list of length 2 representing the resolution i.e. (x, y)
   */
   list<i16> get_max_resolution(),

  /* get_current_resolution
   * description: gets the current resolution of this camera
   * returns: a list of length 2 representing the resolution i.e. (x, y)
   */
   list<i16> get_current_resolution(),

  /* set_resolution
   * description: if supported, sets the resolution of the camera
   */
   oneway void set_resolution(1:i16 x, 2:i16 y)
}

/*******************************************************************************
A CameraServer serves as a wrapper around a camera and provides a number of
utility functions for managing the server and camera.
*******************************************************************************/
service CameraServer {
  /* ping
   * description: Used to ping the server.
   * returns: True, always
   */
  bool ping(),

  /* identify
   * description: Gets this server's unique identifier.
   * returns: String containing this server's identifier
   */
  string identify(),

  /* stream_urls
   * description: Gets a list of URL where the stream of this server's cameras
                  may be accessed, if they exist.
   * returns: List of strings containing URLs, or an empty list.
   */
  list<string> stream_urls(),

  /* ping
   * description: Shuts down this server. This does not need to be implemented,
   *              but the server must accept the function call.
   */
  oneway void shutdown(),

  /* start_capture
   * description: Captures a still from this server's camera(s) and stores in
                  internally under the given `data_code` for later retrieval.
   */
  oneway void start_capture(1:string data_code),

  /* retrieve_stills_png
   * description: Retrieves .png images that were captured using `start_capture`
                  under the specified `data_code` (if they exist), encoded as
                  PNGs.
   * throws: ImageUnavailable
   * returns: a list of strings, where each string contains one image encoded as
              a PNG file. Each string should be able to be dumped directly to
              the disk and still form a valid PNG file.
   */
  list<string> retrieve_stills_png(1:string with_data_code) throws(1:ImageUnavailable unavailable),

  /* retrieve_stills_jpg
   * description: Retrieves images that were captured using `start_capture`
                  under the specified `data_code` (if they exist), encoded as
                  JPEGs.
   * throws: ImageUnavailable
   * returns: a list of strings, where each string contains one image encoded as
              a JPEG file. Each string should be able to be dumped directly to
              the disk and still form a valid JPEG file.
   */
  list<string> retrieve_stills_jpg(1:string with_data_code) throws(1:ImageUnavailable unavailable),

  /* enumerate_methods
   * description: Returns a dictionary of the methods supported by this server.
                  This is currently not used for any function as of v3,
                  so you may choose to just return an empty dictionary,
                  but be aware that this may change in the future versions.
   * returns: A dictionary with:
               key: method name
               value: a list of argument names that the method takes
   */
  map<string, list<string>> enumerate_methods()
}
