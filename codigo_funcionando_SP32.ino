#include <WiFi.h>
#include <WiFiUdp.h>
#include <SPI.h>
#include <MFRC522.h>

const char* ssid = "toy";
const char* password = "34488455";
const char* serverIP = "192.168.88.237";  // Dirección IP del servidor
const int serverPort = 3008;              // Puerto del servidor
WiFiUDP udp;

#define SS_PIN 5
#define RST_PIN 0

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Instancia de la clase MFRC522

MFRC522::MIFARE_Key key;

// Arreglo para almacenar el nuevo NUID
byte nuidPICC[4];

void setup() {
  Serial.begin(115200);

  // Conexión WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Conectando a WiFi...");
  }
  Serial.println("Conexión WiFi establecida");

  // Inicialización del lector RFID
  SPI.begin();
  mfrc522.PCD_Init();
  Serial.println("Lector RFID inicializado");

  // Inicialización del socket UDP
  udp.begin(0);  // Puerto local aleatorio
  Serial.print("IP local: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Verifica si se detecta una tarjeta RFID
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    String cardData = getCardData();
    sendMessage(cardData);
    mfrc522.PICC_HaltA();  // Detiene la comunicación con la tarjeta RFID
  }
}

String getCardData() {
  String cardData = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    cardData += String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : "");
    cardData += String(mfrc522.uid.uidByte[i], HEX);
  }
  return cardData;
}

void sendMessage(String message) {
  // Envía el mensaje UDP al servidor
  udp.beginPacket(serverIP, serverPort);
  udp.print(message);
  udp.endPacket();
  Serial.println("Mensaje enviado: " + message);
}
