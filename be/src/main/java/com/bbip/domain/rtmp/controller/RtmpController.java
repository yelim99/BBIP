package com.bbip.domain.rtmp.controller;

import com.bbip.domain.rtmp.Dto.StreamKeyDto;
import com.bbip.domain.rtmp.Dto.StreamListDto;
import com.bbip.domain.rtmp.service.RtmpService;
import com.bbip.global.exception.InvalidParamException;
import com.bbip.global.exception.NoSelectedRtmpServerException;
import com.bbip.global.response.ListResponse;
import com.bbip.global.response.SingleResponse;
import io.swagger.v3.oas.annotations.Operation;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/rtmps")
@Slf4j
public class RtmpController {

    private final RtmpService rtmpService;

    @Operation(
            summary = "스트림키 수정",
            description = "입력 객체 속성에 스트리밍서버 id와 스트림키 입력 필요"
    )
    @PostMapping
    public SingleResponse<StreamKeyDto> modifyStreamKey(
            @RequestHeader(value = "Authorization", required = false) String accessToken,
            @RequestBody StreamKeyDto rtmpDto) {

        if (rtmpDto.getServerId() == 0 || rtmpDto.getServerId() > 8) {
            throw new InvalidParamException("[지원하지 않는 서버 ID] 유효한 값: 1 ~ 8");
        }

        StreamKeyDto result = rtmpService.updateStreamkey(accessToken, rtmpDto);

        return SingleResponse.<StreamKeyDto>builder()
                .message("스트림키 업데이트 완료")
                .data(result).build();
    }

    @Operation(
            summary = "송출 설정 가능한 스트림 서버 목록 조회",
            description = "어떤 스트리밍 서버로 송출을 할지 선택하기 위한 목록으로, 스트림키에 대한 정보가 등록된 플랫폼 목록이 반환됨"
    )
    @GetMapping
    public ListResponse<StreamKeyDto> findAll(@RequestHeader(value = "Authorization", required = false) String accessToken) {

        List<StreamKeyDto> result = rtmpService.getServers(accessToken);

        return ListResponse.<StreamKeyDto>builder()
                .message("스트림키 정보가 있는 서버 목록")
                .dataList(result).build();
    }

    @Operation(
            summary = "송출할 서버 설정",
            description = "송출을 결정한 서버 id의 목록을 \"servers\" 속성에 배열 형태로 입력"
    )
    @PostMapping(value = "/streamList")
    public ListResponse<StreamKeyDto> modifyStreamList(
            @RequestHeader(value = "Authorization", required = false) String accessToken,
            @RequestBody StreamListDto streamList) {

        for (Integer serverId : streamList.getServers()) {
            if (serverId == 0 || serverId > 8) { throw new InvalidParamException("[지원하지 않는 서버 ID] 유효한 값: 1 ~ 8"); }
        }

        List<StreamKeyDto> result = rtmpService.updateStreamList(accessToken, streamList);

        return ListResponse.<StreamKeyDto>builder()
                .message("수정된 스트리밍 예정 서버 목록")
                .dataList(result).build();
    }

}
