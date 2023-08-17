const Gpio = require('pigpio').Gpio; 
const cron = require('node-cron')
const axios = require('axios')
var delay = require('sleep');
const raspiInfo = require('raspberry-info');
const rpiStatus = require('rpi-status');
const Pwm = require('pigpio').Gpio;

//pin gpio
const servopin = new Gpio(12, {mode: Gpio.OUTPUT});
const echo1Pin = new Gpio(15, {mode: Gpio.INPUT, alert: true});
const trigger1Pin = new Gpio(14, {mode: Gpio.OUTPUT});
const ldrpin = new Gpio(26, {mode: Gpio.INPUT, alert: true});
const lamp1pin = new Gpio(23, {mode: Gpio.OUTPUT});
const lamp2pin = new Gpio(14, {mode: Gpio.OUTPUT});

var blynkserver = `sgp1.blynk.cloud`
var blynktoken = `aw7VIwTBK3iBUMwdzmRMJkvOz-tD7hvd`

let distance = ``
let servo = ``
let ldr = ``
let indexldr = ``
let swled1, swled2, swauto, swservo;
let distanceril;
let temp = ``
let servoindex = ``

let startTick1;

let pulseWidth = 1000;
let increment = 100;


function moveServo(direction) {
  if (direction === 'left' && currentPulseWidth < 2000) {
    currentPulseWidth += incrementAmount;
  } else if (direction === 'right' && currentPulseWidth > 1000) {
    currentPulseWidth -= incrementAmount;
  }

  servopin.servoWrite(currentPulseWidth);
}

async function servoclose(){
    servopin.servoWrite(2000);
    servoindex = `Auto Close`
}

async function servoopen(){
    servopin.servoWrite(1000);
    servoindex = `Auto Open`
}

const measureDistance = () => {

    //-------------------------[ READ ATAS ]---------------------------//
    echo1Pin.on('alert', function(level1, tick1) {
      if (level1 === 1) {
        startTick1 = tick1;
      } else {
        const endTick1 = tick1;
        const diff1 = (endTick1 >> 0) - (startTick1 >> 0); // memotong nilai desimal
  
        // Menghitung jarak dengan rumus: jarak = waktu x kecepatan suara / 2
        const distance1 = diff1 / 2 / 1000000 * 34300;
  
        // Menyimpan data pembacaan ke dalam file database.json
        distanceril = distance1.toFixed(0)
        distance = distanceril.toString()+' cm'
        //console.log(distance)
        //fs.writeFileSync('./lib/database/database.json', JSON.stringify(database))
        //console.log("tutup: ", tutup, "cm");
      }
    });
}

measureDistance() //starting measure

async function readLDR(){
    ldr = ldrpin.digitalRead().toString()
    
    if (ldr == '1'){
        lamp1pin.digitalWrite(1);     
        indexldr = `Gelap`   
        indexlamp = `hidup Auto`                                                                                                         
    } else {
        lamp1pin.digitalWrite(0)  
        indexldr = `Terang`   
        indexlamp = `Mati Auto`
    }
    //console.log(ldr)
}       

cron.schedule('*/1 * * * * *', async () => { //upload data setiap 1 detik
    try{

    const getbin_stat = await axios.get(`https://${blynkserver}/external/api/batch/update?token=${blynktoken}&V1=${distance}&V4=${indexlamp}&V2=${servo}&V3=${indexldr}&V7=${servoindex}`);
  
  } catch(err){
    console.log('upload err')
  }
  });

cron.schedule('*/1 * * * * *', async () => { //read manual switch setiap 1 detik
    try{

    const getbin_stat = await axios.get(`https://${blynkserver}/external/api/get?token=${blynktoken}&V0&V8&V5`);
    swled1 = getbin_stat.data.V0
    swauto = getbin_stat.data.V8
    swservo = getbin_stat.data.V5
    //console.log(swled1)
    //console.log(swauto)


    } catch(err){
        console.log('read switch err')
    }
});

cron.schedule('*/1 * * * * *', async () => { //read manual switch setiap 1 detik
  try{
  rpiStatus.getAll().then((result) => {
    temp = result.cpuTemp + ' °C'
  })
  const getbin_stat = await axios.get(`https://${blynkserver}/external/api/update?token=${blynktoken}&V6=${temp}`);
  } catch(err){
    console.log('read system err')
}
});

  // Loop measure
setInterval(() => {
      trigger1Pin.trigger(10, 1);
      if(swauto == '1'){
        readLDR();
        if(distanceril < 20){
          servo = `terlalu dekat!`
          //servo set on
          servoopen();
          //servopin.servoWrite(2000); 
          //moveServo('left')
      
        } else if(distanceril > 20 && distanceril <30){
          servo = `jarak dekat`
        } else {
          //servo set off
          servoclose();
          //servopin.servoWrite(1000);
          servo = `jarak aman`
          //moveServo('right')
          
        }
      } else {
        if(swled1 == '1'){
            lamp1pin.digitalWrite(1);  
            indexldr = `Sedang mode manual` 
            indexlamp = `hidup Manual`
        } else {
            lamp1pin.digitalWrite(0); 
            indexldr = `Sedang mode manual`  
            indexlamp = `mati manual`
        }

        if(swservo == '1'){
          servopin.servoWrite(1000);
          servoindex = `Manual Open`
          servo = `Sedang mode manual`
        } else {
          servopin.servoWrite(2000);
          servoindex = `Manual Close`
          servo = `Sedang mode manual`
        }
      }
    }, 100);
  