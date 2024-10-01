package com.bbip.domain.signalling.controller;

import lombok.extern.slf4j.Slf4j;
import org.springframework.messaging.handler.annotation.DestinationVariable;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.stereotype.Controller;

@Controller
@Slf4j
public class SignalController {

    //client to ai
   @MessageMapping("client/ai/{key}")
   @SendTo("sub/ai/client/{key}")
   public String clientToAi(@DestinationVariable String key, @Payload String message) {
       return message;
   }

    //client to encoder
    //ai to encoder

    //ai to client
    //encoder to client
    //encoder to ai

    @MessageMapping("/cam/{key}")
    @SendTo("/sub/client/{key}")
    public String camToClient(@DestinationVariable("key") String key, @Payload String message) {
        log.info("message: " + message);
        return message;
    }

    @MessageMapping("/client/{key}")
    @SendTo("/sub/cam/{key}")
    public String clientToCam(@DestinationVariable("key") String key, @Payload String message) {
        log.info("message: " + message);
        return message;
    }

    @MessageMapping("/message")
    @SendTo("/sub/message")
    public String signal(String message) {
        log.info("message: " + message);
        return message;
    }
}