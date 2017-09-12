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
A CameraServer serves as a wrapper around a camera and provides a number of
utility functions for managing the server and camera.
*******************************************************************************/
service CameraServer{
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
   * returns: A dictionary where:
               key: method name
               value: a list of argument names that the method takes
   */
  map<string, list<string>> enumerate_methods()
}
