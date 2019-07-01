  '''
  creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
  if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
      creds = pickle.load(token)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
      creds = flow.run_local_server()
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
      pickle.dump(creds, token)
      
  service = build('docs', 'v1', credentials=creds)
  print("in createnote")
  title = 'Test Doc'
  body = {
    'title': title
  }
  doc = service.documents() \
    .create(body=body).execute()
  print('Created document with title: {0}'.format(
    doc.get('title')))
  '''
  
  '''
  g_login = GoogleAuth()
  
  auth_url = g_login.GetAuthUrl() # Create authentication url user needs to visit
  code = g_login.AskUserToVisitLinkAndGiveCode() # Your customized authentication flow
  g_login.Auth(code) # Authorize and build service from the code
  
  g_login.LoadCredentialsFile("credentials.json")
  if g_login.credentials is None:
    print("HERE")
    g_login.LocalWebserverAuth()
    print("After")
  elif g_login.access_token_expired:
    g_login.Refresh()
  else:
    g_login.Authorize()
  
    
  g_login.SaveCredentialsFile("credentials.json")

  drive = GoogleDrive(g_login)
  

  file1 = drive.CreateFile({'title': 'Hello'})  # Create GoogleDriveFile instance with title 'Hello.txt'.
  file1.SetContentString('Hello World!') # Set content of the file from given string.
  file1.Upload()
  '''