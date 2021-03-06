import picamera
import picamera.mmal as mmal

# 覆盖PiVideoEncoder以跟踪每种类型的帧数量
class MyEncoder(picamera.PiCookedVideoEncoder):
    def start(self, output, motion_output=None):
        self.parent.i_frames = 0
        self.parent.p_frames = 0
        super(MyEncoder, self).start(output, motion_output)

    def _callback_write(self, buf):
        # 只在缓冲区表明帧结束并且不是SPS / PPS标头（..._ CONFIG）时才计数
        if (
                (buf.flags & mmal.MMAL_BUFFER_HEADER_FLAG_FRAME_END) and
                not (buf.flags & mmal.MMAL_BUFFER_HEADER_FLAG_CONFIG)
            ):
            if buf.flags & mmal.MMAL_BUFFER_HEADER_FLAG_KEYFRAME:
                self.parent.i_frames += 1
            else:
                self.parent.p_frames += 1
        # 记得返回父级函数的结果！
        return super(MyEncoder, self)._callback_write(buf)

# 覆盖PiCamera以使自定义编码器开始录制视频
class MyCamera(picamera.PiCamera):
    def __init__(self):
        super(MyCamera, self).__init__()
        self.i_frames = 0
        self.p_frames = 0

    def _get_video_encoder(
            self, camera_port, output_port, format, resize, **options):
        return MyEncoder(
                self, camera_port, output_port, format, resize, **options)

with MyCamera() as camera:
    camera.start_recording('foo4_15.h264')
    camera.wait_recording(10)
    camera.stop_recording()
    print('Recording contains %d I-frames and %d P-frames' % (
            camera.i_frames, camera.p_frames))