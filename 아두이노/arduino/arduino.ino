#include <SoftwareSerial.h>
#include <MsTimer2.h>
//#include <avr/interrut.h>
#include <String.h>

SoftwareSerial BTSerial(2, 3);  // 소프트웨어 시리얼 포트(TX, RX)

float LED[3] = {0,};  
float db[100] = {0,};
float time[100] = {0,};

int endPoint = 0;

void setup() {
  Serial.begin(9600); 
  BTSerial.begin(9600);  
}

void loadData() {
  float data = 0;
  int index = 0;
  int dbIndex = 0, timeIndex = 0;

  while (true) {
    data = BTSerial.parseFloat(); // 앱 인벤터에서 넘어온 값 float로 변환해 읽기
    if(index <3){ // 최초로 들어오는 3개의 숫자는 각각 R, G, B의 limit을 결정
      LED[index] = data;
      index++;
      continue;
    }

    if (data == -1){
      endPoint = dbIndex;
      break; // 만약 -1일 경우 while 문 탈출 (-1 == 데이터의 마지막 숫자)
    }

    if (index % 2 == 0) time[dbIndex++] = data; // index가 짝수일 경우 time에 저장
    else if (index % 2 == 1) db[timeIndex++] = data; // index가 홀수일 경우 db에 저장
    index++;
  }
  Serial.println("데시벨 1번 인덱스 75.~");
  Serial.println(db[1]);
}

void changeLED(float brightness) {
  analogWrite(9, brightness * LED[0]); 
  analogWrite(10, brightness* LED[1]); 
  analogWrite(11, brightness* LED[2]); 
}

void loop() {

  while(true){
      char read;
      while (BTSerial.available()) {
        read = BTSerial.read(); // 한 글자만 읽기
        if (read == 'S') { 
          loadData(); // 데이터 load
          Serial.println("send received"); // load 완료 확인
          break; // 다음 반복문으로 갈거임
        }
      }
      if(read == 'S') break;
  }

  int index = 0;
  while(true){
    changeLED(db[index]);
    Serial.println(db[index]);
    Serial.println(time[index]);
    delay(time[index]*1000);
    index++;
    if(index == endPoint) break;
  }

} 




















