package com.bbip.domain.user.controller;

import com.bbip.domain.user.dto.UserDto;
import com.bbip.domain.user.service.UserServiceImpl;
import com.bbip.global.response.CommonResponse;
import com.bbip.global.response.SingleResponse;
import io.swagger.v3.oas.annotations.Operation;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
@Slf4j
public class UserController {

    private final UserServiceImpl userService;

    @Operation(
            summary = "사용자 정보 수정",
            description = "모든 필드 값 필수"
    )
    @PostMapping
    public SingleResponse<UserDto> modifyUser(@RequestHeader(value = "Authorization", required = false) String accessToken,
                                              @RequestBody UserDto user) {

        UserDto modifiedUser = userService.updateUser(accessToken, user);
        return SingleResponse.<UserDto>builder().
                message("사용자 정보 수정 완료").data(modifiedUser).build();
    }

    @Operation(
            summary = "사용자 정보 조회",
            description = "accessToken을 사용해 사용자 정보 조회"
    )
    @GetMapping
    public SingleResponse<UserDto> getUserDetail(@RequestHeader(value = "Authorization", required = false) String accessToken) {

        UserDto userDetail = userService.getUserDetail(accessToken);
        return SingleResponse.<UserDto>builder().
                message("유저 상세정보 조회 성공").data(userDetail).build();
    }

    @Operation(
            summary = "사용자 탈퇴",
            description = "accessToken을 사용해 사용자 탈퇴처리"
    )
    @DeleteMapping
    public CommonResponse deleteUser(@RequestHeader(value = "Authorization", required = false) String accessToken) {

        userService.deleteUser(accessToken);
        return new CommonResponse("유저 탈퇴 처리 완료");
    }
}
