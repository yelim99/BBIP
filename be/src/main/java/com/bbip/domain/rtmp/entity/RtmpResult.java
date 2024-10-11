package com.bbip.domain.rtmp.entity;

public interface RtmpResult {

    Integer getUserId();
    Integer getServerId();
    String getServerName();
    String getServerUri();
    String getKey();
    Boolean getStream();

}
