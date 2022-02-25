#include <Wire.h>
#include <UIPEthernet.h>

#define DAC_ADDR 0x60
#define MAX_VOLT 5.0f

bool manualIP = true;
IPAddress myIP(192,168,0,141);
uint16_t port = 80;
uint8_t mac[6] = {0x00,0x01,0x02,0x03,0x04,0x05};
EthernetServer server = EthernetServer(port);
bool ethOK = false;
bool reply = true;


void setup_eth()
{
    ethOK = (Ethernet.linkStatus() != 0);
    if(ethOK)
    {
        if(!manualIP)
        {
            if(Ethernet.begin(mac) == 0)
            {
                Serial.println("DHCP failed");
                Ethernet.begin(mac, myIP);
            }
        }
        else
        {
            Ethernet.begin(mac, myIP);
        }
      
        server.begin();

        Serial.print("Interface MAC: ");
        for (byte i = 0; i < 6; ++i)
        {
            Serial.print(mac[i], HEX);
            if (i < 5)
            {
              Serial.print(':');
            }
        }
        Serial.println("");
        Serial.print("Listening on IP: ");
        Serial.print(Ethernet.localIP());
        Serial.print(", on port ");
        Serial.println(port);
        Serial.println("Ready!");
    }
    else
    {
      Serial.println("Ethernet error");
    }
}

void setup_wire()
{
    Wire.begin(DAC_ADDR);
    Wire.setClock(400000L);
}

void sendResponse(EthernetClient client, int code, char extra[]="")
{
    client.print("HTTP/1.1 ");
    client.println(code);
    client.println();
    client.print(extra);
}

void set_dac_v(uint16_t output)
{
    Wire.beginTransmission(DAC_ADDR);
    Wire.write(0x40);

    Wire.write(output >> 4);
    Wire.write((output & 0xF) << 4);
    Wire.endTransmission();
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
    // Initialize serial communication:
    Serial.begin(9600);
    
    // Initialize DAC Wire control (I2C)
    setup_wire(); 

    // Initialize ethernet communications
    setup_eth();
}

void listen_serial()
{
    if (Serial.available() == 2)
    {
        byte buffer[2];
        Serial.readBytes(buffer, 2);
        uint16_t val = (buffer[1] << 8) | (buffer[0]);
        set_dac_v(validate_12bit(val));
    }
}

void listen_eth()
{
    int size;
    if (EthernetClient client = server.available())
    {
        if(client.connected())
        {
            size = (int)client.available();
            if(size != 0)
            {
                char* msg = (char*)malloc(size + 1);
                size = (int)client.read(msg, size);
                msg[size] = 0x00;
                char* pcmd = strstr(msg, "\r\n\r\n");
                if(pcmd != NULL)
                {
                    pcmd += 4;
                    int cmd_size = size - (pcmd - msg);
                    if(cmd_size > 0)
                    {
                        char* p_setid = strstr(msg, "set ");
                        if(p_setid != NULL)
                        {
                            p_setid += 4;
                            set_dac_v(validate_12bit((uint16_t)atoi(p_setid)));
                            sendResponse(client, 200, p_setid);
                        } 
                        else
                        {
                            char* p_setid = strstr(msg, "test");
                            if(p_setid != NULL)
                            {
                                sendResponse(client, 200, p_setid);
                            }
                            else
                            {
                                sendResponse(client, 400);
                            }
                            
                        }
                    }
                    else
                    {
                        sendResponse(client, 400);
                    }
                }
                else
                {
                    sendResponse(client, 400);
                }
                free(msg);
            }
        }
    
        delay(100);
        client.stop();
    }
}

void loop() {
    // Listen for incoming messages through serial port
    listen_serial();

    // Listen for incoming messages through ethernet
    listen_eth();
}
