const express = require('express')
const path = require('path')
const fs = require('fs')
const app = express()
const port = 80;

app.use('/static',express.static('static'));
app.use(express.urlencoded())//help data of form to reach express

//pug is help to create html from raw format
//set template engin as pug
//app.set('view engine','index.html');

//set the view directory
app.set('views',path.join(__dirname,'views'))
app.engine('html',require('ejs').renderFile);
app.set('view engine','html');

//endpoint
app.get('/',(req,res)=>{
    const con = "Humanity is ment to born on earth, but never ment to die here!"
    const params = {'title':'Interstellar','content':con};
    res.status(200).render('home.html',params);
})
app.get('/contact',(req,res)=>{
    const con = "Humanity is ment to born on earth, but never ment to die here!"
    const params = {'title':'Interstellar','content':con};
    res.status(200).render('contact.html',params);
})
app.get('/sign',(req,res)=>{
    const con = "Humanity is ment to born on earth, but never ment to die here!"
    const params = {'title':'Interstellar','content':con};
    res.status(200).render('sign.html',params);
})
app.get('/display',(req,res)=>{
    const con = "Humanity is ment to born on earth, but never ment to die here!"
    const params = {'title':'Interstellar','content':con};
    res.status(200).render('display.html',params);
})
app.get('/user',(req,res)=>{
    const con = "Humanity is ment to born on earth, but never ment to die here!"
    const params = {'title':'Interstellar','content':con};
    res.status(200).render('user.html',params);
})
app.post('/contact',(req,res)=>{
    console.log(req.body)
    const params = {'message':'Form Submitted successfully'};

    res.status(200).render('contact.html',params);
    name=req.body.name
    email=req.body.email
    Phno=req.body.Phno
    desc=req.body.desc
    gender=req.body.gender
    address=req.body.address

    let output = `The name of client is ${name} with gender ${gender} with ${email} with ${Phno} having resident address ${address} with consern as ${desc}.`
    fs.writeFileSync('database/output.txt',output)//file will be created of submitted data from user.

})
app.post('/sign',(req,res)=>{
    console.log(req.body)
    const params = {'message':'Form Submitted successfully'};

    res.status(200).render('sign.html',params);

})
app.listen(port,()=>{


    console.log(`this is listing on port ${port}`);
 })
    