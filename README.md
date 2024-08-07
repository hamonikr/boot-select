![ubuntu-bionic](https://img.shields.io/badge/ubuntu-18.04-red)
![ubuntu-focal](https://img.shields.io/badge/ubuntu-20.04-red)
![ubuntu-hirsute](https://img.shields.io/badge/ubuntu-21.04-red)
![ubuntu-jammy](https://img.shields.io/badge/ubuntu-22.04-red)
![ubuntu-noble](https://img.shields.io/badge/ubuntu-24.04-red)

![hamonikr-me](https://img.shields.io/badge/hamonikr-me-orange)
![hamonikr-sun](https://img.shields.io/badge/hamonikr-sun-blue)
![hamonikr-jin](https://img.shields.io/badge/hamonikr-jin-green)
![hamonikr-hanla](https://img.shields.io/badge/hamonikr-hanla-purple)
![hamonikr-kumkang](https://img.shields.io/badge/hamonikr-kumkang-blue)

[![Build Status](https://github.com/hamonikr/boot-select/actions/workflows/ci.yml/badge.svg)](https://github.com/hamonikr/boot-select/actions/workflows/ci.yml)


## boot-select

PC에 여러개의 다른 운영체제나 여러개의 커널을 설치한 경우, 기본으로 부팅 될 메뉴를 선택하는 프로그램입니다.

 * Ubuntu, Debian, LinuxMint 사용 가능.

![boot-select](docs/boot-select.png)


## Usage
 * 프로그램 > boot-select
 * 또는 터미널에서 sudo boot-select
 * 기본값으로 설정을 원하는 부팅메뉴를 선택하면 자동으로 재시작


## Install

### Ubuntu, Debian, LinuxMint

터미널을 열고(Ctrl+Alt+T) 아래 명령어를 입력하세요.

```
wget -qO- https://pkg.hamonikr.org/add-hamonikr.apt | sudo -E bash -

sudo apt install boot-select
```

## License
 * Apache 2.0
 
## 기타 버그 또는 이슈 

사용 중 발견한 버그나 이슈는 [이슈 페이지](https://github.com/hamonikr/boot-select/issues) 또는 [하모니카 커뮤니티](https://hamonikr.org)에서 공유해주세요.
