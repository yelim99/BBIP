package com.bbip.domain.signalling.message;

public class SignalMessage {

    private String type;
    private String data;

    public SignalMessage(String type, String data) {
        this.type = type;
        this.data = data;
    }
}