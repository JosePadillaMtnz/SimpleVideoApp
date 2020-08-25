class conn_param:

    def __init__(self):
        self.video_reception = 0
        self.audio_reception = 0
        self.video_destination = 0
        self.audio_destination = 0
        self.direction_ip_destination = "0.0.0.0"
        self.direction_ip_local = "0.0.0.0"

    def setVideoReception(self, video):
        self.video_reception = video

    def getVideoReception(self):
        return self.video_reception

    def getVideoReceptionRtcp(self):
        return self.video_reception+1

    def setAudioReception(self, audio):
        self.audio_reception = audio

    def getAudioReception(self):
        return self.audio_reception

    def getAudioReceptionRtcp(self):
        return self.audio_reception+1

    def setVideoDestination(self, video):
        self.video_destination = video

    def getVideoDestination(self):
        return self.video_destination

    def getVideoDestinationRtcp(self):
        return self.video_destination+1

    def setAudioDestination(self, audio):
        self.audio_destination = audio

    def getAudioDestination(self):
        return self.audio_destination

    def getAudioDestinationRtcp(self):
        return self.audio_destination+1

    def setDireccionIpLocal(self, dir):
        self.direction_ip_local = dir

    def getDireccionIpLocal(self):
        return self.direction_ip_local

    def setDireccionIpDestination(self, dir):
        self.direction_ip_destination = dir

    def getDireccionIpDestination(self):
        return self.direction_ip_destination

    def __toString__(self):
        print("\nValues of current conection:")
        print("\tPort video reception / Port video reception Rtcp = %d / %d" % (self.video_reception, self.video_reception + 1))
        print("\tPort audio reception / Port audio reception Rtcp = %d / %d" % (self.audio_reception, self.audio_reception + 1))
        print("\tPort video destination / Port video destination Rtcp = %d / %d" % (self.video_destination, self.video_destination + 1))
        print("\tPort audio destination / Port audio destination Rtcp = %d / %d" % (self.audio_destination, self.audio_destination + 1))
        print("\tDirection ip local = %s" % (self.direction_ip_local))
        print("\tDirection ip destination = %s \n" % (self.direction_ip_destination))

    def correctValues(self):
        sepd = self.direction_ip_destination.split(".")
        sepr = self.direction_ip_local.split(".")
        if (self.audio_destination%2 != 0 or self.audio_reception%2 != 0 or self.video_destination%2 != 0 or self.video_reception%2 != 0):
            return "Only pair ports are valid. Please set values again."
        elif (self.audio_destination == self.audio_reception or self.audio_destination == self.video_destination or self.audio_destination == self.video_reception or self.audio_reception == self.video_destination or self.audio_reception == self.video_reception or self.video_reception == self.video_destination):
            return "Only different ports are valid. Please set values again."
        elif (sepd.__len__() != 4 or sepr.__len__() != 4):
            return "Format of ip directions are wrong. Please set values again."
        else:
            for i in [0,1,2,3]:
                if (int(sepd[i]) < 0 or int(sepd[i]) > 255 or int(sepr[i]) < 0 or int(sepr[i]) > 255):
                    return "Values of direction ip are out of range. Please set values again."
        return "Correct values"

    