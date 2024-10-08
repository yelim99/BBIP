package com.bbip.domain.rtmp.service;

import com.bbip.domain.rtmp.Dto.StreamKeyDto;
import com.bbip.domain.rtmp.Dto.StreamListDto;
import com.bbip.domain.rtmp.entity.RtmpResult;
import com.bbip.domain.rtmp.entity.RtmpServerEntity;
import com.bbip.domain.rtmp.entity.StreamKeyEntity;
import com.bbip.domain.rtmp.entity.StreamKeyIdEntity;
import com.bbip.domain.rtmp.repository.RtmpServerRepository;
import com.bbip.domain.rtmp.repository.StreamKeyRepository;
import com.bbip.domain.user.entity.UserEntity;
import com.bbip.domain.user.repository.UserRepository;
import com.bbip.global.exception.NoSelectedRtmpServerException;
import com.bbip.global.exception.RtmpServerNotFoundException;
import com.bbip.global.util.JwtUtil;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Optional;

@Service
@Slf4j
@RequiredArgsConstructor
public class RtmpServiceImpl implements RtmpService {

//    private static final String PREFIX = "[f=flv]";
    private final StreamKeyRepository streamKeyRepository;
    private final UserRepository userRepository;
    private final RtmpServerRepository serverRepository;
    private final JwtUtil jwtUtil;

    @Override
    public List<String> getRtmpUrls(String accessToken) {

        // JWT토큰에서 사용자 id 추출
        int userId = jwtUtil.getUserIdFromJWT(accessToken);
        List<RtmpResult> rtmpResults = streamKeyRepository.findStreamRtmpUrl(userId);
        if (rtmpResults.isEmpty()) {
            throw new NoSelectedRtmpServerException("송출하도록 설정된 서버가 한 개 이상 있어야 합니다.");
        }

        List<String> result = new ArrayList<>();
        for (RtmpResult rtmpResult : rtmpResults) {
            result.add(rtmpResult.getServerUri() + rtmpResult.getKey());
        }

        log.info("송출 대상 url 목록 조회 : {}", result.toString());
        return result;
    }

    @Override
    @Transactional
    public StreamKeyDto updateStreamkey(String accessToken, StreamKeyDto streamKeyDto) {

        // JWT토큰에서 사용자 id 추출
        int userId = jwtUtil.getUserIdFromJWT(accessToken);

        UserEntity userEntity = userRepository.findById(userId);
        Optional<RtmpServerEntity> rtmpServerEntity = serverRepository.findById(streamKeyDto.getServerId());

        // 유저-rtmp서버의 복합키 생성
        StreamKeyIdEntity streamKeyId = StreamKeyIdEntity.builder()
                                            .userId(userId)
                                            .serverId(streamKeyDto.getServerId()).build();

        if (streamKeyDto.getStreamKey().isBlank() || streamKeyDto.getStreamKey().isEmpty()) {
            streamKeyRepository.deleteStreamKey(userId, streamKeyDto.getServerId());
            log.info("스트림키 삭제");
        } else {
            streamKeyRepository.save(
                    StreamKeyEntity.builder()
                            .id(streamKeyId)
                            .userEntity(userEntity)
                            .serverEntity(rtmpServerEntity.orElseThrow())
                            .key(streamKeyDto.getStreamKey())
                            .stream(false).build()
            );
            log.info("스트림키 업데이트 완료");
        }

        return streamKeyDto;
    }

    @Override
    public List<StreamKeyDto> getServers(String accessToken) {

        // JWT토큰에서 사용자 id 추출
        int userId = jwtUtil.getUserIdFromJWT(accessToken);

        List<RtmpResult> rtmpResults = streamKeyRepository.findAllRtmpUrl(userId);
        if (rtmpResults.isEmpty()) {
            throw new RtmpServerNotFoundException("해당 유저의 송출 가능한 스트리밍 서버 없음. 스트림키 등록 필요");
        }
        List<StreamKeyDto> DtoResult = new ArrayList<>();
        for (RtmpResult rtmpResult : rtmpResults) {
            DtoResult.add(StreamKeyDto.builder()
                    .serverId(rtmpResult.getServerId())
                    .streamKey(rtmpResult.getKey()).build());
        }
        return DtoResult;
    }

    @Override
    @Transactional
    public List<StreamKeyDto> updateStreamList(String accessToken, StreamListDto streamList) {

        // JWT토큰에서 사용자 id 추출
        int userId = jwtUtil.getUserIdFromJWT(accessToken);

        List<RtmpResult> rtmpResults = streamKeyRepository.findAllRtmpUrl(userId);
        if (rtmpResults.isEmpty()) {
            throw new RtmpServerNotFoundException("해당 유저의 송출가능한 스트리밍 서버 없음. 스트림키 등록 필요");
        }

        List<StreamKeyDto> DtoResult = new ArrayList<>();
        for (RtmpResult rtmpResult : rtmpResults) {
            if (streamList.getServers().contains(rtmpResult.getServerId())) {
                streamKeyRepository.updateStreamKey(userId, rtmpResult.getServerId(), true);
                DtoResult.add(new StreamKeyDto(rtmpResult.getServerId(), rtmpResult.getKey()));
            } else {
                streamKeyRepository.updateStreamKey(userId, rtmpResult.getServerId(), false);
            }
        }
        return DtoResult;
    }
}
