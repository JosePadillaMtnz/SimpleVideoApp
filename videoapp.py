import conn_parameter as connection,gi,sys,threading,time
gi.require_version('Gst', '1.0')
from gi.repository import Gst,GLib
conn = connection.conn_param()
running = True
buffers = {}

connStats = {
    "video_bitrate_average": "0",
    "video_packets_received": "0",
    "video_octets_received": "0",
    "video_jitter_average": "0",
    "video_packets_to_des": "0",
    "audio_bitrate_average": "0",
    "audio_packets_received": "0",
    "audio_octets_received": "0",
    "audio_jitter_average": "0",
    "audio_packets_to_des": "0",
}

def getConnValues(conn): #Function for initial values
    correct = False
    print("Set connection values using pair ports and without repeating ports.")
    while(not correct):
        print("Set port video destination:")
        conn.setVideoDestination(int(input()))
        print("Set port video reception:")
        conn.setVideoReception(int(input()))
        print("Set port audio destination:")
        conn.setAudioDestination(int(input()))
        print("Set port audio reception:")
        conn.setAudioReception(int(input()))
        print("Set local direction ip:")
        conn.setDireccionIpLocal(input())
        print("Set destination direction ip:")
        conn.setDireccionIpDestination(input())
        value = conn.correctValues()
        if (value.startswith("Correct")): correct = True
        else: print(value)
    conn.__toString__()

def video_send(pipeline,rtpbin): #Function to send video
    video = Gst.ElementFactory.make('v4l2src')
    pipeline.add(video)
    convert = Gst.ElementFactory.make('videoconvert')
    pipeline.add(convert)
    rate = Gst.ElementFactory.make('videorate')
    pipeline.add(rate)
    filter = Gst.ElementFactory.make('capsfilter')
    caps = Gst.Caps.from_string('video/x-raw,width=640, \
                                 height=480,framerate=25/1, \
                                 format=I420')
    filter.set_property('caps',caps)
    pipeline.add(filter)
    x264 = Gst.ElementFactory.make('x264enc')
    x264.set_property('speed-preset','ultrafast')
    x264.set_property('tune','zerolatency')
    x264.set_property('bitrate',2000)
    x264.set_property('key-int-max',25)
    pipeline.add(x264)
    h264pay = Gst.ElementFactory.make('rtph264pay')
    h264pay.set_property('pt',96)
    h264pay.set_property('config-interval',1)
    pipeline.add(h264pay)
    queue = Gst.ElementFactory.make('queue')
    pipeline.add(queue)
    rtp = Gst.ElementFactory.make('udpsink')
    rtp.set_property('host',conn.getDireccionIpDestination())
    rtp.set_property('port',conn.getVideoDestination())
    pipeline.add(rtp)
    rtcp = Gst.ElementFactory.make('udpsink')
    rtcp.set_property('host',conn.getDireccionIpDestination())
    rtcp.set_property('port',conn.getVideoDestinationRtcp())
    rtcp.set_property('sync','false')
    rtcp.set_property('async','false')
    pipeline.add(rtcp)
    l1 = video.link(convert)
    l2 = convert.link(rate)
    l3 = rate.link(filter)
    l4 = filter.link(x264)
    l5 = x264.link(h264pay)
    l6 = h264pay.link(queue)
    l7 = queue.link_pads('src',rtpbin,'send_rtp_sink_0')
    l8 = rtpbin.link_pads('send_rtp_src_0',rtp,'sink')
    l9 = rtpbin.link_pads('send_rtcp_src_0',rtcp,'sink')
    return l1 and l2 and l3 and l4 and l5 and l6 and l7 and l8 and l9

def video_receiver(pipeline,rtpbin): #Function to receive video
    udpsrc = Gst.ElementFactory.make('udpsrc')
    udpsrc.set_property('port',conn.getVideoReception())
    caps = Gst.Caps.from_string('application/x-rtp, \
                             media=video, clock-rate=90000, \
                             encoding-name=H264')
    udpsrc.set_property('caps',caps)
    pipeline.add(udpsrc)
    rtph264depay = Gst.ElementFactory.make('rtph264depay','rtph264depay')
    pipeline.add(rtph264depay)
    queue = Gst.ElementFactory.make('queue')
    pipeline.add(queue)
    avdec_h264 = Gst.ElementFactory.make('avdec_h264')
    pipeline.add(avdec_h264)
    videoconvert = Gst.ElementFactory.make('videoconvert')
    pipeline.add(videoconvert)
    autovideosink = Gst.ElementFactory.make('autovideosink')
    pipeline.add(autovideosink)
    l1 = udpsrc.link_pads('src',rtpbin,'recv_rtp_sink_0')
    l2 = rtph264depay.link(queue)
    l3 = queue.link(avdec_h264)
    l4 = avdec_h264.link(videoconvert)
    l5 = videoconvert.link(autovideosink)
    return l1 and l2 and l3 and l4 and l5

def audio_send(pipeline,rtpbin): #Function to send audio
    audio = Gst.ElementFactory.make('autoaudiosrc')
    pipeline.add(audio)
    filter = Gst.ElementFactory.make('capsfilter')
    caps = Gst.Caps.from_string('audio/x-raw,channels=2, \
                                 rate=48000,format=F32LE')
    filter.set_property('caps',caps)
    pipeline.add(filter)
    convert = Gst.ElementFactory.make('audioconvert')
    pipeline.add(convert)
    aac = Gst.ElementFactory.make('avenc_aac')
    aac.set_property('bitrate',64000)
    pipeline.add(aac)
    mp4apay = Gst.ElementFactory.make('rtpmp4apay')
    mp4apay.set_property('pt',97)
    pipeline.add(mp4apay)
    queue = Gst.ElementFactory.make('queue')
    pipeline.add(queue)
    rtp = Gst.ElementFactory.make('udpsink')
    rtp.set_property('host',conn.getDireccionIpDestination())
    rtp.set_property('port',conn.getAudioDestination())
    pipeline.add(rtp)
    rtcp = Gst.ElementFactory.make('udpsink')
    rtcp.set_property('host',conn.getDireccionIpDestination())
    rtcp.set_property('port',conn.getAudioDestinationRtcp())
    rtcp.set_property('sync','false')
    rtcp.set_property('async','false')
    pipeline.add(rtcp)
    l1 = audio.link(filter)
    l2 = filter.link(convert)
    l3 = convert.link(aac)
    l4 = aac.link(mp4apay)
    l5 = mp4apay.link(queue)
    l6 = queue.link_pads('src',rtpbin,'send_rtp_sink_1')
    l7 = rtpbin.link_pads('send_rtp_src_1',rtp,'sink')
    l8 = rtpbin.link_pads('send_rtcp_src_1',rtcp,'sink')
    return l1 and l2 and l3 and l4 and l5 and l6 and l7 and l8

def audio_receiver(pipeline,rtpbin): #Function to receive audio
    udpsrc = Gst.ElementFactory.make('udpsrc')
    udpsrc.set_property('port',conn.getAudioReception())
    caps = Gst.Caps.from_string('application/x-rtp, \
                             media=audio,encoding-name=MP4A-LATM, \
                             clock-rate=48000,config=40002320adca00')
    udpsrc.set_property('caps',caps)
    pipeline.add(udpsrc)
    rtpmp4adepay = Gst.ElementFactory.make('rtpmp4adepay','rtpmp4adepay')
    pipeline.add(rtpmp4adepay)
    queue = Gst.ElementFactory.make('queue')
    pipeline.add(queue)
    avdec_aac = Gst.ElementFactory.make('avdec_aac')
    pipeline.add(avdec_aac)
    audioconvert = Gst.ElementFactory.make('audioconvert')
    pipeline.add(audioconvert)
    autoaudiosink = Gst.ElementFactory.make('autoaudiosink')
    pipeline.add(autoaudiosink)
    l1 = udpsrc.link_pads('src',rtpbin,'recv_rtp_sink_1')
    l2 = rtpmp4adepay.link(queue)
    l3 = queue.link(avdec_aac)
    l4 = avdec_aac.link(audioconvert)
    l5 = audioconvert.link(autoaudiosink)
    return l1 and l2 and l3 and l4 and l5

def rtcp_receiver(pipeline,rtpbin,port1,port2): #Function to receive RTCP reports
    src1 = Gst.ElementFactory.make('udpsrc')
    src1.set_property('port',port1)
    pipeline.add(src1)
    src2 = Gst.ElementFactory.make('udpsrc')
    src2.set_property('port',port2)
    pipeline.add(src2)
    l1 = src1.link_pads('src',rtpbin,'recv_rtcp_sink_0')
    l2 = src2.link_pads('src',rtpbin,'recv_rtcp_sink_1')
    return l1 and l2

def on_pad_added(rtpbin, pad, pipeline): 
    name = pad.get_name()
    depay = None

    if name.startswith('recv_rtp_src_0'): #Video session
        depay = pipeline.get_by_name('rtph264depay')
        rtcp = Gst.ElementFactory.make('udpsink')
        rtcp.set_property('host',conn.getDireccionIpDestination())
        rtcp.set_property('port',conn.getVideoDestinationRtcp())
        rtcp.set_property('sync','false')
        rtcp.set_property('async','false')
        pipeline.add(rtcp)
        rtpbin.link_pads('send_rtcp_src_0',rtcp,'sink')

    elif name.startswith('recv_rtp_src_1'): #Audio session
        depay = pipeline.get_by_name('rtpmp4adepay')
        rtcp = Gst.ElementFactory.make('udpsink')
        rtcp.set_property('host',conn.getDireccionIpDestination())
        rtcp.set_property('port',conn.getAudioDestinationRtcp())
        rtcp.set_property('sync','false')
        rtcp.set_property('async','false')
        pipeline.add(rtcp)
        rtpbin.link_pads('send_rtcp_src_1',rtcp,'sink')

    if depay:
        pad_sink = depay.sinkpads[0]
        pad.link(pad_sink)

def parse_stats(struct,typee,level=1): #Stats function
    for i in range(0,struct.n_fields()):
        n = struct.nth_field_name(i)
        v = struct.get_value(n)
        if isinstance(v,Gst.Structure):
            parse_stats(v,typee,level+4)
        elif isinstance(v,list) and v:
            for e in v:
                parse_stats(e,typee,level+4)
        else:
            if ("bitrate" in n and typee == 0 and int(v) > 0):
                connStats["video_bitrate_average"] = v
            if ("bitrate" in n and typee == 1 and int(v) > 0):
                connStats["audio_bitrate_average"] = v
            if ("octets-received" in n and typee == 0 and int(v) > 0):
                connStats["video_octets_received"] = v
            if ("octets-received" in n and typee == 1 and int(v) > 0):
                connStats["audio_octets_received"] = v
            if ("packets-received" in n and typee == 0 and int(v) > 0):
                connStats["video_packets_received"] = v
            if ("packets-received" in n and typee == 1 and int(v) > 0):
                connStats["audio_packets_received"] = v
            if ("avg-jitter" in n and typee == 0 and int(v) > 0):
                connStats["video_jitter_average"] = v
            if ("avg-jitter" in n and typee == 1 and int(v) > 0):
                connStats["audio_jitter_average"] = v
            if ("num-pushed" in n and typee == 0 and int(v) > 0):
                connStats["video_packets_to_des"] = v
            if ("num-pushed" in n and typee == 1 and int(v) > 0):
                connStats["audio_packets_to_des"] = v

def check_session(rtpbin): #Stats function
    while running:
        sesion0 = rtpbin.emit('get-session',0)
        statsVideo = sesion0.get_property('stats')
        parse_stats(statsVideo,0)

        sesion1 = rtpbin.emit('get-session',1)
        statsAudio = sesion1.get_property('stats')
        parse_stats(statsAudio,1)

        time.sleep(1)

def on_new_jitterbuffer(rtpbin,jitterbuffer,session,ssrc): #Jitter function
    buffers[session] = jitterbuffer

def check_buffers(): #Jitter function
    while running:
        for session in buffers:
            buffer = buffers[session]
            stats = buffer.get_property('stats')
            parse_stats(stats,session)
        time.sleep(1)

def showStructure():
    while running:
        time.sleep(10)
        print("Live audio and video statistics of the current connection:")
        print("-- Video stats")
        print("---- Average bitrate: ", connStats["video_bitrate_average"])
        print("---- Packets received: ", connStats["video_packets_received"])
        print("---- Octets received: ", connStats["video_octets_received"])
        print("---- Average jitter: ", connStats["video_jitter_average"])
        print("---- Number of packets sent to the unpacker: ", connStats["video_packets_to_des"])
        print("-- Audio stats")
        print("---- Average bitrate: ", connStats["audio_bitrate_average"])
        print("---- Packets received: ", connStats["audio_packets_received"])
        print("---- Octets received: ", connStats["audio_octets_received"])
        print("---- Average jitter: ", connStats["audio_jitter_average"])
        print("---- Number of packets sent to the unpacker: ", connStats["audio_packets_to_des"])

if __name__ == "__main__":
    getConnValues(conn) 
    Gst.init(sys.argv)

    pipeline = Gst.Pipeline.new("pipeline") #Pipeline to receive data
    rtpbin = Gst.ElementFactory.make('rtpbin')
    rtpbin.connect('pad-added', on_pad_added, pipeline)
    rtpbin.connect('new-jitterbuffer',on_new_jitterbuffer)
    pipeline.add(rtpbin)
    r1 = video_receiver(pipeline,rtpbin) #Function to receive video
    r2 = audio_receiver(pipeline,rtpbin) #Function to receive audio
    r3 = rtcp_receiver(pipeline,rtpbin,conn.getVideoReceptionRtcp(),conn.getAudioReceptionRtcp()) #Function to receive RTCP reports

    pipeline2 = Gst.Pipeline.new("pipeline") #Pipeline to send data
    rtpbin2 = Gst.ElementFactory.make("rtpbin")
    pipeline2.add(rtpbin2)
    r4 = video_send(pipeline2,rtpbin2) #Function to send video
    r5 = audio_send(pipeline2,rtpbin2) #Function to send audio
    r6 = rtcp_receiver(pipeline2,rtpbin2,conn.getVideoDestinationRtcp(),conn.getAudioDestinationRtcp()) #Function to receive RTCP reports

    if r1 and r2 and r3 and r4 and r5 and r6:
        pipeline.set_state(Gst.State.PLAYING)
        pipeline2.set_state(Gst.State.PLAYING)
        loop = GLib.MainLoop()
        jitter = threading.Thread(target=check_buffers)
        stats = threading.Thread(target=check_session,args=[rtpbin])
        showStats = threading.Thread(target=showStructure)

        try:        
            jitter.start()
            stats.start()
            showStats.start()
            loop.run()        
        except KeyboardInterrupt:
            pass

        pipeline.set_state(Gst.State.NULL)
        pipeline2.set_state(Gst.State.NULL)
        running = False
        jitter.join()
        stats.join()
        showStats.join()

    else:
        print('Error:',r1,r2,r3,r4,r5,r6)