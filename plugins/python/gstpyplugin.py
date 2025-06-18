#!/usr/bin/env python3
import logging
import gi

gi.require_version('Gst', '1.0')
gi.require_version('GObject', '2.0')
from gi.repository import Gst, GObject

Gst.init(None)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("PyPlugin")


class PyPlugin(Gst.Element):
    __gstmetadata__ = (
        "PyPlugin",
        "Template PyPlugin",
        "Prints the Buffer",
        "Shir Bar-Dagan"
    )

    __gsttemplates__ = (
        Gst.PadTemplate.new(
            "sink", Gst.PadDirection.SINK, Gst.PadPresence.ALWAYS,
            Gst.Caps.new_any()
        ),
        Gst.PadTemplate.new(
            "src", Gst.PadDirection.SRC, Gst.PadPresence.ALWAYS,
            Gst.Caps.new_any()
        )
    )


    def __init__(self):
        super(PyPlugin, self).__init__()
        self.sinkpad = Gst.Pad.new_from_template(self.get_pad_template("sink"), "sink")
        self.srcpad = Gst.Pad.new_from_template(self.get_pad_template("src"), "src")
        
        self.sinkpad.set_chain_function_full(self.chainfunc)

        self.add_pad(self.sinkpad)
        self.add_pad(self.srcpad)

    def push_buffer_to_srcpad(self, buff: bytes) -> Gst.FlowReturn:
        try:
            out_buffer = Gst.Buffer.new_allocate(None, len(buff), None)
            out_buffer.fill(0, buff)

            self.srcpad.push(out_buffer)
            return Gst.FlowReturn.OK
        except Exception as e:
            logger.error("While pushing buffer to src pad: %s", e)
            return Gst.FlowReturn.ERROR

    def chainfunc(self, pad: Gst.Pad, parent: Gst.Object, buffer: Gst.Buffer) -> Gst.FlowReturn:
        """
        Chain function called when a buffer is received on the sink pad.

        Args:
            pad (Gst.Pad): The sink pad receiving the buffer.
            parent (Gst.Object): The parent GStreamer object.
            buffer (Gst.BufferList): The buffer in sink pad.
        Returns:
            Gst.FlowReturn: GST_FLOW_OK on success, GST_FLOW_ERROR on failure.
        """
        success, map_info = buffer.map(Gst.MapFlags.READ)
        try:
            data = bytes(map_info.data)
            logger.debug(f"Received buffer of size {len(data)} bytes: {data[:32]}...")
            
            ret = self.push_buffer_to_srcpad(data)
            return ret
        except Exception as e:
            logger.error("While handling buffer in sink pad: %s", e)
        finally:
            buffer.unmap(map_info)
        


GObject.type_register(PyPlugin)
__gstelementfactory__ = ("pyplugin", Gst.Rank.NONE, PyPlugin)
