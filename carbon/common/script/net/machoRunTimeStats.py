import blue
import uthread
import collections
SAMPLE_RATE = 5000
HISTORY_LENGHT = 2000

class MachoRunTimeStats:
    __guid__ = 'macho.MachoRunTimeStats'

    def __init__(self):
        self.stop = False
        self.worker = None



    def Enable(self):
        self.stop = False
        self.last = [0,
         0,
         0,
         0,
         0,
         0,
         0,
         0]
        self.maxValues = [0,
         0,
         0,
         0,
         0,
         0,
         0,
         0]
        self.history = collections.deque(maxlen=HISTORY_LENGHT)
        self.packetsSendPerSecond = 0
        self.packetsReceivedPerSecond = 0
        self.totalPacketsPerSecond = 0
        self.KBIn = 0
        self.KBOut = 0
        self.movementPacketsReceived = 0
        self.movementPacketsSent = 0
        self.movementPacketsReceivedSize = 0
        self.movementPacketsSentSize = 0
        self.maxPacketsSendPerSecond = 0
        self.maxPacketsReceivedPerSecond = 0
        self.maxTotalPacketsPerSecond = 0
        self.maxKBIn = 0
        self.maxKBOut = 0
        self.maxMovementPacketsReceived = 0
        self.maxMovementPacketsSent = 0
        self.maxMovementPacketsReceivedSize = 0
        self.maxMovementPacketsSentSize = 0
        self.lastupdate = blue.os.GetTime()
        self.worker = uthread.new(self.Worker)



    def Disable(self):
        self.stop = True
        if self.worker:
            self.worker.kill()
            self.worker = None



    def Worker(self):
        while not self.stop:
            delta = blue.os.TimeDiffInMs(self.lastupdate) / 1000L
            self.lastupdate = blue.os.GetTime()
            values = self.last[:]
            mn = sm.services['machoNet']
            self.last[0] = mn.dataSent.Count()
            self.last[1] = mn.dataReceived.Count()
            self.last[2] = mn.dataSent.Current()
            self.last[3] = mn.dataReceived.Current()
            self.last[4] = blue.statistics.GetSingleStat('Aperture/PacketsSent')
            self.last[5] = blue.statistics.GetSingleStat('Aperture/PacketsReceived')
            self.last[6] = blue.statistics.GetSingleStat('Aperture/PacketsSentSize')
            self.last[7] = blue.statistics.GetSingleStat('Aperture/PacketsReceivedSize')
            if delta != 0:
                self.packetsSendPerSecond = float(self.last[0] - values[0]) / delta
                self.packetsReceivedPerSecond = float(self.last[1] - values[1]) / delta
                self.totalPacketsPerSecond = self.packetsSendPerSecond + self.packetsReceivedPerSecond
                self.KBIn = float(self.last[2] - values[2]) / delta
                self.KBOut = float(self.last[3] - values[3]) / delta
                self.movementPacketsSent = float(self.last[4] - values[4]) / delta
                self.movementPacketsReceived = float(self.last[5] - values[5]) / delta
                self.movementPacketsSentSize = float(self.last[6] - values[6]) / delta
                self.movementPacketsReceivedSize = float(self.last[7] - values[7]) / delta
                self.maxPacketsSendPerSecond = max(self.maxPacketsSendPerSecond, self.packetsSendPerSecond)
                self.maxPacketsReceivedPerSecond = max(self.maxPacketsReceivedPerSecond, self.packetsReceivedPerSecond)
                self.maxTotalPacketsPerSecond = max(self.maxTotalPacketsPerSecond, self.totalPacketsPerSecond)
                self.maxKBIn = max(self.maxKBIn, self.KBIn)
                self.maxKBOut = max(self.maxKBOut, self.KBOut)
                self.maxMovementPacketsReceived = max(self.maxMovementPacketsReceived, self.movementPacketsReceived)
                self.maxMovementPacketsSent = max(self.maxMovementPacketsSent, self.movementPacketsSent)
                self.maxMovementPacketsReceivedSize = max(self.maxMovementPacketsReceivedSize, self.movementPacketsReceivedSize)
                self.maxMovementPacketsSentSize = max(self.maxMovementPacketsSentSize, self.movementPacketsSentSize)
                self.history.append((blue.os.GetTime(),
                 self.packetsSendPerSecond,
                 self.packetsReceivedPerSecond,
                 self.KBIn,
                 self.KBOut,
                 self.movementPacketsReceived,
                 self.movementPacketsSent,
                 self.movementPacketsReceivedSize,
                 self.movementPacketsSentSize))
            blue.pyos.synchro.Sleep(SAMPLE_RATE)





