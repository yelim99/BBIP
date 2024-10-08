package com.bbip.domain.user.service;

import com.bbip.domain.user.dto.UserDto;
import com.bbip.domain.user.entity.UserEntity;
import com.bbip.domain.user.repository.UserRepository;
import com.bbip.global.exception.NotSameUserException;
import com.bbip.global.util.JwtUtil;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
@RequiredArgsConstructor
@Slf4j
public class UserServiceImpl implements UserService {

    private final UserRepository userRepository;
    private final JwtUtil jwtUtil;

    @Override
    public UserDto saveOrUpdateOAuthUser(String email, String name, String provider) {
        Optional<UserEntity> existingUser = userRepository.findUser(email, provider);

        // 기존 사용자가 없으면 새로 저장
        if (existingUser.isEmpty()) {
            UserEntity user = UserEntity.builder()
                    .name(name)
                    .email(email)  // AES 암호화 적용됨
                    .nickname(name)
                    .deleted(false)
                    .oauthProvider(provider).build();

            log.info("new user: {}", user);
            return userRepository.save(user).toDto();
        }

        log.info("existing user: {}", existingUser.get());
        return existingUser.get().toDto();  // 이미 등록된 사용자는 그대로 반환
    }

    @Override
    public UserDto updateUser(String accessToken, UserDto user) {
        // JWT토큰에서 사용자 id 추출
        int userId = jwtUtil.getUserIdFromJWT(accessToken);
        if (userId != user.getId()) {
            throw new NotSameUserException("접근한 유저와 수정하려는 유저의 정보가 다릅니다.");
        }
        UserEntity userEntity = userRepository.save(user.toEntity());
        log.info("유저 정보 수정: {}", userEntity);

        return userEntity.toDto();
    }

    @Override
    public UserDto getUserDetail(String accessToken) {

        // JWT토큰에서 사용자 id 추출
        int userId = jwtUtil.getUserIdFromJWT(accessToken);

        UserEntity userEntity = userRepository.findById(userId);
        log.info("유저 조회: {}", userEntity);

        return userEntity.toDto();
    }

    @Override
    @Transactional
    public void deleteUser(String accessToken) {
        // JWT토큰에서 사용자 id 추출
        int userId = jwtUtil.getUserIdFromJWT(accessToken);

        userRepository.signOut(userId);
    }
}
