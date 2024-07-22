#include <SoftwareSerial.h>

SoftwareSerial BTSerial(2, 3);  // 소프트웨어 시리얼 포트(TX, RX)

float LED[3] = { 0, }; // LED의 색감 저장 
float db[150] = { 0, }; // 소리의 db 저장
float time[150] = { 0, }; // db의 유지시간 저장 

int pins[3] = {9, 10, 11}; // LED 출력 핀 설정
int A0PIN = 0; // 조도센서 아날로그 입력 핀
int endPoint = 0; // 끝 인덱스 설정
int light = 0; // 현재 밝기 설정 (외부 밝기에 대한 가산값)

void setup() {
  Serial.begin(9600); // 시리얼 통신 시작
  BTSerial.begin(9600); // 블루투스 통신 시작
}

void loadData() {
  float data = 0; // 데이터 저장 변수
  int index = 0; // 데이터의 인덱스
  int dbIndex = 0, timeIndex = 0; // db와 time의 인덱스

  while (true) {
    // 앱 인벤터에서 넘어온 값 float로 변환해 읽기
    data = BTSerial.parseFloat();  
    // 최초로 들어오는 3개의 숫자는 각각 R, G, B의 limit을 결정
    if (index < 3) { 
      LED[index] = data;
      index++;
      continue;
    }
    // 만약 -1일 경우 while 문 탈출 (-1 == 데이터의 마지막 숫자)
    if (data == -1) {
      endPoint = dbIndex;
      break;  
    }
    // index가 짝수일 경우 time에 저장
    if (index % 2 == 0) time[dbIndex++] = data;       
    // index가 홀수일 경우 db에 저장
    else if (index % 2 == 1) db[timeIndex++] = data; 
    index++;
  }
}

void changeLED(float brightness) {
  // LED의 색을 변경 

  // 밝기에 따른 R, G, B 값 설정
  float R = brightness * LED[0]; 
  float G = brightness * LED[1];
  float B = brightness * LED[2];

  // 조도센서 또는 수동 조절에 따른 밝기 설정
  R += light;
  G += light;
  B += light;

  // R, G, B 값이 0보다 작을 경우 0으로 설정
  if (R <= 0) { R = 0; }
  if (G <= 0) { G = 0; }
  if (B <= 0) { B = 0; }

  // R,G,B 값을 LED에 출력
  analogWrite(pins[0], R);
  analogWrite(pins[1], G);
  analogWrite(pins[2], B);
}

void lightFormat(int photoresistor) {
  // 조도센서에서 읽어온 값을 light scale로 변환 
  if (photoresistor < 300) {
    light = -10;
  } else if (photoresistor < 400) {
    light = -20;
  } else if (photoresistor < 500) {
    light = -30;
  } else if (photoresistor < 600) {
    light = -50;
  } else if (photoresistor < 700) {
    light = -100;
  } 
}

void waiting() {
  char read = ""; // 읽어온 값 저장
  int brightness = 0; // 밝기 저장
  int pinIndex = 0; // 현재 조절 중인 핀의 인덱스
  bool mode = true; // 처음에는 밝기 증가 설정

  while (true) {
    while (BTSerial.available()) {
      read = BTSerial.read(); // 한 글자만 읽기

      if (read == 'S') {
        loadData(); // 데이터 load
        Serial.println("send received"); // load 완료 확인
        BTSerial.print("E");
        break;  // 다음 반복문으로 갈거임
      }
    }

    // 모드에 따라 밝기 증가 또는 감소
    if (mode) { 
      brightness++; // 밝기 증가
      if (brightness >= 255 + light) { // 밝기가 255를 넘어가면
        mode = false; // 밝기 감소
      }
    } else {
      brightness--; // 밝기 감소
      if (brightness <= 0) { // 밝기가 0보다 작아지면
        mode = true; // 밝기 증가
        pinIndex = (pinIndex + 1) % 3; // 다음 핀으로 변경
      }
    }

    analogWrite(pins[pinIndex], brightness);  // 핀의 밝기 설정
    delay(20); // 약간의 지연
    if (read == 'S') break;   // read에 S 입력 시 waiting 종료
  }
}

void clear(){
  while(BTSerial.available()) { // 버퍼에 들어있던 내용 삭제 
      char c = BTSerial.read(); // 버퍼에 있는 값을 읽어옴
      delay(1);  // 1ms 대기 (너무 빠른 속도로 읽어오면 버퍼에 있는 값이 제대로 삭제되지 않을 수 있음)
  }
}

void loop() {
  char read = ""; // 읽어온 값 저장
  int index = 0; // 현재 인덱스
  int value = 0; // 수동 모드일 경우 값 저장
  bool flag = true; // 모드 변경 플레그
  int laytency = 50;

  waiting(); // 대기 모드로 전환

  delay(1000); // 1초 대기 (앱 인벤터에서 데이터를 받을 시간을 주기 위해), 다만 매 블루투스 연결시 차이가 있음

  clear(); // 버퍼에 있는 값 삭제하는 함수
  
  while (index != endPoint) { // 끝 인덱스까지 반복

    if(BTSerial.available()){ // 버퍼에 데이터가 있을 경우
      read = BTSerial.read(); // 지속적으로 앱인벤터에서 값을 받아옴
      value = BTSerial.parseInt(); // 지속적으로 앱인벤터에서 값을 받아옴

      clear(); // 버퍼에 있는 값 삭제하는 함수

      if (read == 'T') break; // S 입력 시 음악 패턴 출력 종료
      
      if (read == 'C') { // 앱인벤터에서 C 입력 시
        flag = false; // 수동 모드로 변경
      }
    }

    if (flag){ // 자동 모드일 경우
      lightFormat(analogRead(A0)); // 조도센서 값을 받아와서 light에 저장
    } else{ // 수동 모드일 경우
      lightFormat(value); // 수동 조절 모드일 경우 light에 value 저장
    }
    changeLED(db[index]); // LED 색상 변경
    // 시간만큼 대기 + 아두이노 지연시간, 아두이노 지연시간은 일정하지 않음
    delay((time[index] * 1000) + laytency); 
    laytency -= 1;
    index++; // 다음 인덱스로 이동
  }

  clear();

  flag = true; // 모드 변경 플레그 초기화
  changeLED(0); // LED 색상 초기화
  waiting(); // 대기 모드로 전환
}