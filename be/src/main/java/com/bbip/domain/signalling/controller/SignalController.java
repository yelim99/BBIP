package com.bbip.domain.signalling.controller;

import org.springframework.messaging.handler.annotation.DestinationVariable;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.stereotype.Controller;

@Controller
public class SignalController {

    @MessageMapping("/cam/{key}")
    @SendTo("/sub/client/{key}")
    public String camToClient(@DestinationVariable("key") String key, @Payload String message) {
        return message;
    }

    @MessageMapping("/client/{key}")
    @SendTo("/sub/cam/{key}")
    public String clientToCam(@DestinationVariable("key") String key, @Payload String message) {
        return message;
    }

    @MessageMapping("/message")
    @SendTo("/sub/message")
    public String signal(String message) {
        return message;
    }
}