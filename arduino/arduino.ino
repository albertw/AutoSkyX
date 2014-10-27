/*
 * Sketch to handle Motor Control for focusser and read the IR temperature
 * sensor (and ambient temperature).
 * 
 * Including required text for MLX Library. I didnt get mine from Adafruit,
 * but the library is very useful for this sensor.
 * 
 */
/*************************************************** 
 This is a library example for the MLX90614 Temp Sensor

 Designed specifically to work with the MLX90614 sensors in the
 adafruit shop
 ----> https://www.adafruit.com/products/1748
 ----> https://www.adafruit.com/products/1749

 These sensors use I2C to communicate, 2 pins are required to  
 interface
 Adafruit invests time and resources providing this open source code, 
 please support Adafruit and open-source hardware by purchasing 
 products from Adafruit!

 Written by Limor Fried/Ladyada for Adafruit Industries.  
 BSD license, all text above must be included in any redistribution
 ****************************************************/

#include <Wire.h>
#include <Time.h>  
#include <Adafruit_MLX90614.h>

Adafruit_MLX90614 mlx = Adafruit_MLX90614();

int motor1Pin = 3; // H-bridge leg 1 
int motor2Pin = 4; // H-bridge leg 2 
int speedPin = 9; // H-bridge enable pin 
int mspeed = 0;
int mdelay = 0;

char serialinput;   // for incoming serial data
const byte MAXIMUM_INPUT_LENGTH = 10;
char input[MAXIMUM_INPUT_LENGTH + 1] = { '\0' };
byte currentindex = 0;
byte i = 0;
String str;
char speedbuf[3];
char mdelaybuf[10];
char tmpchar;
time_t t = now();
int running = 0;
int debug = 0;

void setup() {
	Serial.begin(9600);
	Serial.println("MLX90614 based Sky Temperature Sensor");
	Serial.println("L293DNE based Focus Motor Controller");
	mlx.begin();
	pinMode(motor1Pin, OUTPUT);
	pinMode(motor2Pin, OUTPUT);
	pinMode(speedPin, OUTPUT);
}

void loop() {
	// Saftey. If the motor has been running for 5 seconds stop it.
	if (running == 1 && now() - t > 4) {
		digitalWrite(speedPin, LOW);
		running = 0;
		if (debug == 1) {
			Serial.println(t);
			Serial.println(now());
			Serial.println("Motor Emercency STOP!!!!");
		}
	}

	// Resetuthe input buffer
	for (byte i = 0; i <= MAXIMUM_INPUT_LENGTH; i++) {
		input[i] = '\0';
	}
	currentindex = 0;

	while (Serial.available() > 0) {
		// Read in a string up to '\n'
		serialinput = Serial.read();
		while (serialinput != '\n' && currentindex < MAXIMUM_INPUT_LENGTH) {
			input[currentindex++] = serialinput;
			while (Serial.available() < 1) {
			}
			serialinput = Serial.read();
		}
		if (debug == 1) {
			Serial.print("String Recieved:");
			Serial.print(input);
			Serial.print(" length:");
			Serial.println(String(input).length());
		}
		if (String(input).length() == MAXIMUM_INPUT_LENGTH) {
			if (debug == 1) {
				Serial.println(
						"String longer than MACIMUM_INPUT_LENGTH. skipping.");
			}
			break;
		}

		if (String(input) == "q") { // full (5s) left
			move_motor(HIGH, LOW, mspeed, 5000);
		} else if (String(input) == "w") { // holddown mouse left
			move_motor(HIGH, LOW, mspeed, -1);
		} else if (String(input) == "e") { // pulse left
			move_motor(HIGH, LOW, mspeed, mdelay);
		} else if (String(input) == "r") { // stop
			digitalWrite(speedPin, LOW);
			Serial.println("ARDUINO:Stopped motor:");
		} else if (String(input) == "t") { // pulse right
			move_motor(LOW, HIGH, mspeed, mdelay);
		} else if (String(input) == "q") { // holddown mouse right
			move_motor(LOW, HIGH, mspeed, -1);
		} else if (String(input) == "u") { // full (5s) right
			move_motor(LOW, HIGH, mspeed, 5000);
		} else if (String(input) == "c") {
			Serial.print("ARDUINO:Sky:");
			Serial.print(mlx.readObjectTempC());
			Serial.print(":Ambient:");
			Serial.println(mlx.readAmbientTempC());
		} else if (String(input) == "S") {
			// stretch the speed
			Serial.print("ARDUINO:mspeed:");
			Serial.println(int(((float(mspeed) - 100) / 155) * 255));
		} else if (String(input) == "D") {
			// TODO un stretch this value
			Serial.print("ARDUINO:mdelay:");
			Serial.println(mdelay);
		} else if (input[0] == 's') {
			/* We let the external software define a speed from 0-255
			 * However we know that the practical limits are 100-255. So we scale it.
			 */
			mspeed = int((float(get_input_number(input)) / 255) * 155 + 100);
			if (mspeed < 100 || mspeed > 255) { // If we get a wierd speed we set to 0
				mspeed = 0;
			}
			if (debug == 1) {
				Serial.print("Speed determined:");
				Serial.println(mspeed);
			}
			Serial.print("ARDUINO:mspeed:");
			Serial.println(int(((float(mspeed) - 100) / 155) * 255));
		} else if (input[0] == 'd') {
			mdelay = get_input_number(input);
			if (mdelay > 5000) { // We should never move for more than 5 seconds
				mdelay = 5000;
			}
			if (debug == 1) {
				Serial.print("Motor Delay determined:");
				Serial.println(mdelay);
			}
			Serial.print("ARDUINO:mdelay:");
			Serial.println(mdelay);
		}
	}
}

void move_motor(int pin1, int pin2, int mspeed, int mdelay) {
	digitalWrite(motor1Pin, pin1); // set leg 1 of the H-bridge low
	digitalWrite(motor2Pin, pin2); // set leg 2 of the H-bridge high
	analogWrite(speedPin, mspeed);
	if (mdelay != -1) {
		delay(mdelay);
		digitalWrite(speedPin, LOW);
		Serial.println("ARDUINO:Moved motor:");
	} else {
		t = now();
		running = 1;
		Serial.println("ARDUINO:Moved motor: STILL RUNNING!!!!");
	}
}

int get_input_number(char *input) {
	int i = 2;
	char tmpchar;
	char outbuf[32];

	tmpchar = input[1]; //1
	outbuf[0] = tmpchar; //1
	while (tmpchar != '\0') {
		tmpchar = input[i];
		outbuf[i - 1] = tmpchar;
		i++;
	}
	return (String(outbuf).toInt());
}

