import { useState } from 'react';
import './App.css';

const uuid = require('uuid');

function App() {
  const [image, setImage] = useState('');
  const [uploadResultMessage, setUploadResultMessage] = useState('Upload image to authenticate.')
  const [imgName, setImgName] = useState('placeholder.png')
  const [isAuth, setIsAuth] = useState(false);

  //take image from frontend and send it to the visitor s3 bucket, then authenticate
  function sendImage(e) {
    e.preventDefault();
    setImgName(image.name);

    const visitorImageName = uuid.v4();

    fetch(`https://r192ll7u53.execute-api.us-east-1.amazonaws.com/dev/jnvisitor-facial-images/${visitorImageName}.jpg`, { 
      method: 'PUT',
      headers: {
        'Content-Type': 'image/jpg', 
      },
      body: image
    }).then(async () => {
      const response = await authenticate(visitorImageName);

      if (response.Message === 'Success') {
        setIsAuth(true);
        setUploadResultMessage(`Hello ${response['firstName']} ${response['lastName']}. You are authenticated.`)
      }else{
        setIsAuth(false);
        setUploadResultMessage('Authentication Failed')
      }
    }).catch(err => {
      setIsAuth(false);
      setUploadResultMessage('There is an error during the authentication process. Please try again.')
      console.error(err); 
    })
  }

  //check if the jpg has the same face content as the facial images in the employee s3 bucket
  async function authenticate(visitorImageName) {
    const requestUrl = 'https://r192ll7u53.execute-api.us-east-1.amazonaws.com/dev/employee?' + new URLSearchParams({
      objectKey: `${visitorImageName}.jpg`
    });
    return await fetch(requestUrl, {
      method: 'GET',
      headers:{
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    }).then(response => response.json())
    .then((data) => {
      return data;
    }).catch(err => console.error(err));
  }

  return (
    <div className="App">
      <h1>AWS Facial Recognition System</h1>
      <form onSubmit={sendImage}>
        <input type='file' name='image' onChange={e => setImage(e.target.files[0])}/>
        <button type='submit'>Authenticate</button>
      </form>
      <div className={isAuth ? 'success' : 'failure'}>{uploadResultMessage}</div>
      <img src={ require(`./visitors/${imgName}`)} alt='VisitorImage' height={250} width={250}/>
    </div>
  );
}

export default App;
