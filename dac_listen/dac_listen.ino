#include <Wire.h>

#define DAC_ADDR 0x60
#define MAX_VOLT 5.0f

bool reply = true;


void normal_mode(uint16_t output)
{
    Wire.beginTransmission(DAC_ADDR);
    Wire.write(0x40);

    Wire.write(output >> 4);
    Wire.write((output & 0xF) << 4);
    Wire.endTransmission();
}

void fast_mode(uint16_t output1, uint16_t output2)
{
    Wire.beginTransmission(DAC_ADDR);

    Wire.write(output1 >> 8);
    Wire.write(output1 & 0xFF);
    Wire.write(output2 >> 8);
    Wire.write(output2 & 0xFF);
    Wire.endTransmission();
}

float uint2volt(uint16_t intval)
{
    float val = MAX_VOLT*intval/4095.0;    
    return val;
}

uint16_t validate_12bit(uint16_t val)
{
    if(val > 4095)
    {
        val = 4095;
    }
    if(val < 0)
    {
        val = 0;
    }

    return val;
}

void setup() {
    // Initialize DAC Wire control (I2C)
    Wire.begin(DAC_ADDR);
    Wire.setClock(400000L);

    // Set initial voltage to 0
    // It seems setup is run again when external communication ceases.
    //normal_mode(0);
    
    // initialize serial communication:
    Serial.begin(9600);
}

void loop() {
    if (Serial.available() == 2)
    {
        byte buffer[2];
        Serial.readBytes(buffer, 2);

        if((char)buffer[0] == 'r')
        {
            if((char)buffer[1] == 'y')
            {
              reply = true;
              Serial.println("Detected enable replies command");
            }
            if((char)buffer[1] == 'n')
            {
              reply = false;
              Serial.println("Detected suppress replies command");
            }
        }
        else
        {
            uint16_t val = (buffer[1] << 8) | (buffer[0]);
            normal_mode(validate_12bit(val));

            if(reply)
            {
                Serial.print("Received: ");
                Serial.println(val);
                Serial.print("Voltage set: ");
                Serial.print(uint2volt(val));
                Serial.println(" V.");
            }  
        }
    }
    //delay(10);
}
