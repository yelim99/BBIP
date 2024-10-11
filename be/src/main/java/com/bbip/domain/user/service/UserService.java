package com.bbip.domain.user.service;

import com.bbip.domain.user.dto.UserDto;

public interface UserService {
    UserDto saveOrUpdateOAuthUser(String email, String name, String provider);
    UserDto updateUser(String accessToken, UserDto user);
    UserDto getUserDetail(String accessToken);
    void deleteUser(String accessToken);
}
