package com.bbip.domain.rtmp.service;

import com.bbip.domain.rtmp.Dto.StreamKeyDto;
import com.bbip.domain.rtmp.Dto.StreamListDto;

import java.util.List;

public interface RtmpService {
    List<String> getRtmpUrls(String accessToken);

    StreamKeyDto updateStreamkey(String accessToken, StreamKeyDto rtmpDto);

    List<StreamKeyDto> getServers(String accessToken);

    List<StreamKeyDto> updateStreamList(String accessToken, StreamListDto streamList);
}
