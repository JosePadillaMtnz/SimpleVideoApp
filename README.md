## Simple Video Calls Application Code (Python & Gstreamer)
Throughout the development of this code, it is intended to develop a bidirectional videoconferencing application that will work through the command line. We will use a code implemented in Python, in which we will integrate the gstreamer functionality.

### Starting the application
First, we must enter the ports for both receiving and sending audio and video information. We must also enter our own IP address and that of the user with whom we want to make the video call. The application asks you for the information in the following way and in the following order:

- Set port video destination
- Set port video reception
- Set port audio destination
- Set port audio reception
- Set local direction ip
- Set destination direction ip

To make a video call with another user, it is important to note that both of you will have to put the equivalent ports, that is: If a user puts 5000 in the audio destination port, the other user must put that same port in the audio sending. Proceed in the same way with all the previously mentioned parameters.

### Audio and video information
About the audio, 48,000 samples are taken per second. They are in F32LE format and it is stereo type. The codec used is AAC and it is transmitted at a constant rate of 64 Kbps.

About the video, the images exchanged during the call are 640x480 pixels, and the frequency of sending these images is 25 frames per second. The video codec used is H264, running at 2 Mbps bitrate and one key frame per second.

### Connection reports
When the call begins, information related to the status of the call is updated through the execution of different threads. This information is being sent between the two users of the call and can be used to know if there is a problem with the call. We process this information and keep what is really important. Specifically, we show the following information (both audio and video):

- Average bitrate.
- Number of packages received.
- Number of octets received.
- Average jitter.
- Number of packages sent to the unpacker.