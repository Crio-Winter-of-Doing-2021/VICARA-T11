<template>
  <v-container
    id="dashboard-view"
    fluid
    tag="section"
  >
    <v-row justify="center">

      <div class="text-center ma-2">
      <v-snackbar
        v-model="uploadSnack"
      >
        {{ uploadText }}
  
        <template v-slot:action="{ attrs }">
          <v-btn
            color="pink"
            text
            v-bind="attrs"
            @click="uploadSnack= false"
          >
            Close
          </v-btn>
        </template>
      </v-snackbar>
    </div>

    </v-row>


    <v-row justify="center">

      <div class="text-center ma-2">
      <v-snackbar
        v-model="errorSnack"
      >
        {{ errorText }}
  
        <template v-slot:action="{ attrs }">
          <v-btn
            color="pink"
            text
            v-bind="attrs"
            @click="errorSnack= false"
          >
            Close
          </v-btn>
        </template>
      </v-snackbar>
    </div>

    </v-row>


    <v-dialog
        v-model="boolUploadDialog"
        max-width="700px"
        
      >

        
        <v-card>
          <v-card-title>
            <span class="headline">Upload File</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>

                <v-col cols="12">
          
        <input type="file" id="file" ref="file" v-on:change="handleFileUpload()"/>
                </v-col>
                <v-col
                  cols="12"
                >
                
                <v-select
                    :items="['private', 'public']"
                    label="File Access*"
                    v-model="fileScope"
                  ></v-select>
                  <v-autocomplete
                    no-data-text="No folders available by that name"
                    :items="upload_paths"
                    item-value="id"
                    item-text="path"
                    v-model="destinationID_upload"
                    label="Select File Path"
                    
                  ></v-autocomplete>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="blue darken-1"
              text
              @click="boolUploadDialog = false"
            >
              Close
            </v-btn>
            <v-btn
              color="blue darken-1"
              text
              @click="uploadFile"
            >
              Confirm
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

 <v-dialog
        v-model="boolDownloadDialog"
        max-width="700px"
      
        
      >

        
        <v-card>
          <v-card-title>
            <span class="headline">Download </span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>

                <v-col cols="12">
                  <v-text-field
                    label="Download URL"
                    :value="url"
                  ></v-text-field>
                </v-col>
                
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="blue darken-1"
              text
              @click="boolDownloadDialog = false"
            >
              Close
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>


   <v-dialog
        v-model="boolRenameFileDialog"
        max-width="700px"
        
      >

        
        <v-card>
          <v-card-title>
            <span class="headline">Rename File </span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>

                <v-col cols="12">
                  <v-text-field
                    label="Folder Name*"
                    v-model="renameFileName"
                  ></v-text-field>
                </v-col>
                
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="blue darken-1"
              text
              @click="boolRenameFileDialog = false"
            >
              Close
            </v-btn>
            <v-btn
              color="blue darken-1"
              text
              @click="renameFile"
            >
              Confirm
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>



    <v-dialog
        v-model="boolMoveFileDialog"
        max-width="700px"
        
      >

        
        <v-card>
          <v-card-title>
            <span class="headline">Move File To </span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                
                <v-col
                  cols="12"
                >
                
                  <v-autocomplete
                    no-data-text="This is the only folder or no folders available by that name"
                    :items="move_file_paths"
                    item-value="id"
                    item-text="path"
                    v-model="destinationID_moveFile"
                    label="Select Folder Path"
                    
                  ></v-autocomplete>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="blue darken-1"
              text
              @click="boolMoveFileDialog = false"
            >
              Close
            </v-btn>
            <v-btn
              color="blue darken-1"
              text
              @click="moveFile"
            >
              Confirm
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    

    <br>
    <br>
    <br>
    <br>

    <view-intro
      :heading="files.length === 0 ? 'No Files have been starred by you' : 'Starred Files'"
    />
    <v-row>
      
      <v-col
        v-for="({ actionIcon, uploaded_on, details, ...attrs }, i) in files"
        :key="i"
        cols="12"
        md="6"
        lg="3"
      >
        <material-stat-card v-bind="attrs">
          <template #actions>
            <v-icon
              class="mr-2"
              small
              v-text="actionIcon"
            />
            <div class="text-truncate">
              {{ uploaded_on }}
            </div>
            <v-col class="text-right">
            <v-menu
              bottom
              right
            >
              <template v-slot:activator="{ on, attrs }">
                <v-btn
                  icon
                  v-bind="attrs"
                  v-on="on"
                >
                  <v-icon>mdi-menu</v-icon>
                </v-btn>
              </template>
  
              <v-list>
                <v-list-item
                  v-for="({title}, i) in file_utils"
                  :key="i"
                  @click="file_log(title, details)"
                >
                
                  <v-list-item-title v-if="details.scope_type === 'private' && title === 'Make'">Make Public</v-list-item-title>
                  <v-list-item-title v-else-if="details.scope_type === 'public' && title === 'Make'">Make Private</v-list-item-title>
                  <v-list-item-title v-else-if="details.is_starred === 1 && title === 'Favorite'">Unstar File</v-list-item-title>
                  <v-list-item-title v-else-if="details.is_starred === 0 && title === 'Favorite'">Star File</v-list-item-title>
                  <v-list-item-title v-else>{{ title }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
            </v-col>
          </template>
        </material-stat-card>
      </v-col>
    </v-row>



  </v-container>

  
  
</template>

<script>
  // Utilities
  import Vue from 'vue'
  import axios from 'axios'

  const lineSmooth = Vue.chartist.Interpolation.cardinal({
    tension: 0,
  })

  export default {
    name: 'DashboardView',

    data: () => ({
      renameFileID: 0,
      boolRenameFileDialog: false,
      renameFileName: '',
      destinationID_moveFile:0,
      boolMoveFileDialog:false,
      move_file_paths: [],
      moveFileID: 0,
      boolDownloadDialog: false,
      url: '',
      uploadSnack: false,
      uploadText: '',
      file: '',
      file_upload: '',
      destinationID_upload: 0, 
      fileScope: '',
      upload_paths: [],
      boolUploadDialog: false,
      files: [],
      errorText : '',
      errorSnack : false,
      createScope: '',
      createFolderName:'',
      boolSnackbarMove: false,
      moveFolderText: '',
      timeout: 2000,
      destinationID_move: 0,
      moveFolderID: 0,
      move_folder_paths: [],
      boolMoveDialog: false,
      boolSnackbarCreate: false,
      createFolderText: '',
      destinationID_create: 0,
      create_folder_paths: [],
      boolCreateDialog : false,
      results : [],
      current_working_directory_id : '',
      current_working_directory_path : '',
      previous_working_directories_id : [],
      previous_working_directories_path : [],
      folders: [
      ],
      boolRenameFolderDialog: false,
      renameFolderID:0,
      renameFolderName: '',
      tabs: 0,
      file_utils: [

      { title: 'Download', },
       { title: 'Rename',},
      { title: 'Make', },
      { title: 'Favorite', },
      { title: 'Trash', },
      { title: 'Move To',},
      
    ],
    }), 
    methods:{
      file_log(string, details) {
        if(string === 'Make') {
          this.changeFileScope(details)
        } else if (string === 'Favorite') {
          if(details.is_starred === 1) {
            this.unstarFile(details)
          } else if(details.is_starred == 0) {
            this.starFile(details)
          } 
        } else if (string === 'Download') {
          this.downloadFile(details)
        } else if (string === 'Move To') {
          this.moveFileID = details.id
          this.getMoveFilePaths(details)
        } else if(string === 'Trash') {
          this.trashFiles(details)
        } else if(string === 'Rename') {
          this.renameFileID = details.id
          this.renameFileInit()
        }
    
  
      },
      renameFileInit() {
        this.boolRenameFileDialog = true
      },
      renameFile() {
        let file_name = this.renameFileName
        file_name = file_name.trim()
        const file_id = this.renameFileID
        if (file_name === '') {
          this.createFolderText = 'Please fill all details'
          this.boolSnackbarCreate = true
          this.boolRenameFileDialog = false
          return 
        }
        this.boolRenameFileDialog = false
        const TOKEN = localStorage.getItem('token')
          axios.patch(`http://localhost:8000/files/rename?file_id=${file_id}&newfilename=${file_name}`,
            {

            },
            {
            headers: {
            'Authorization': `Bearer ${TOKEN}`,
            },
          })
          .then((response) => {
            if(response.data === file_id) {
              for(let i = 0; i < this.files.length; i++){
                if(this.files[i]["details"]["id"] === file_id) {
                this.files[i]["value"] = file_name
                break;
              }
          }
            }
          })
          .catch((error) => {
            if(error.response.status === 404) {
              this.errorText = 'The file does not exist.'
              this.errorSnack = true
            } else if(error.response.status === 409) {
              this.errorText = 'The file with that name already exists in the directory.'
              this.errorSnack = true
            } else {
              this.errorText = 'An error occured while processing your request.'
              this.errorSnack = true
            }
            });

      },
      downloadFile(details) {
        const TOKEN = localStorage.getItem('token')
        axios.get(`http://localhost:8000/files/download?file_id=${details.id}`, {
        headers: {
          'Authorization': `Bearer ${TOKEN}`,
        },
        })
        .then((response) => {
        const data = response.data;
        this.url = data["download_url"]
        this.boolDownloadDialog = true
        
        
        })
        .catch((error) => {
            if(error.response.status === 404) {
              this.errorText = 'The file does not exist.'
              this.errorSnack = true
            } else {
              this.errorText = 'An error occured while processing your request.'
              this.errorSnack = true
            }
        

        })


      },
      unstarFile(details) {
          const TOKEN = localStorage.getItem('token')
          axios.patch(`http://localhost:8000/files/unstar?file_id=${details.id}`,
            {

            },
            {
            headers: {
            'Authorization': `Bearer ${TOKEN}`,
            },
          })
          .then((response) => {
            if(response.status === 204) {
              let index = -1 
              for(let i = 0; i < this.files.length; i++){
                if(this.files[i]["details"]["id"] === details.id) {
                index = i
                this.files[i]["details"]["is_starred"] = 0
                break;
              }
            }
            this.files.splice(index,1)
            }
          })
          .catch((error) => {
            if(error.response.status === 404) {
              this.errorText = 'The file does not exist.'
              this.errorSnack = true
            } else {
              this.errorText = 'An error occured while processing your request.'
              this.errorSnack = true
            }
            });
      },
      starFile(details) {
          const TOKEN = localStorage.getItem('token')
          axios.patch(`http://localhost:8000/files/star?file_id=${details.id}`,
            {

            },
            {
            headers: {
            'Authorization': `Bearer ${TOKEN}`,
            },
          })
          .then((response) => {
            if(response.status === 204) {
              for(let i = 0; i < this.files.length; i++){
                if(this.files[i]["details"]["id"] === details.id) {
                this.files[i]["details"]["is_starred"] = 1
                break;
              }
          }
            }
          })
          .catch((error) => {
              if( error.response.status === 404) {
              this.errorText = 'The file does not exist.'
              this.errorSnack = true
            } else {
              this.errorText = 'An error occured while processing your request.'
              this.errorSnack = true
            }
            });
      },
      handleFileUpload(){
        this.file = this.$refs.file.files[0];
      },
      uploadFile() {
        const file_scope = this.fileScope
        const parent_id = this.destinationID_upload
        if (file_scope === '' || parent_id === 0) {
          this.uploadText = 'Please fill all details'
          this.uploadSnack = true
          this.boolUploadDialog = false
          return 
        }
        this.boolUploadDialog = false
        const TOKEN = localStorage.getItem('token')
        let formData = new FormData();
        formData.append("file", this.file);

        axios.post(`http://localhost:8000/files/upload?folder_id=${parent_id}&scope=${file_scope}`,
            formData,{
            headers: {
            'Authorization': `Bearer ${TOKEN}`,
            'Content-Type': 'multipart/form-data'
            },
          })
          .then((response) => {
            if(response.status === 200) {
              this.uploadText = 'The file has been uploaded'
              this.uploadSnack = true
              const file_data = response.data
              let file = {
                actionIcon: 'mdi-clock-outline',
                uploaded_on: 'Uploaded ' + new Date(file_data["uploaded_on"]).toLocaleString(),
                color: '#91e1fb',
                icon: 'mdi-file',
                value: file_data["name"],
                details : {
                  id : file_data["id"],
                  parent_dir_id : file_data["parent_directory_id"],
                  full_path : file_data["full_path"],
                  scope_type : file_data["scope_type"],
                  is_starred: file_data["is_starred"],
                  size_in_gb: file_data["size_in_gb"]
                }

              }
              const temp_path = this.current_working_directory_path
              if (temp_path === file.details["full_path"]) {
                this.files.unshift(file)
              }
            }
          })
          .catch((error) => {
            if(error.response.status === 404) {
              this.boolCreateDialog = false
              this.errorText = 'The folder does not exist.'
              this.errorSnack = true
          } else if (error.response.status === 409){
            this.boolCreateDialog = false
            this.createFolderText = 'The file with given name already exists in the directory'
            this.boolSnackbarCreate = true

          } else{
              this.boolCreateDialog = false
              this.errorText = 'An error occured while processing your request.'
              this.errorSnack = true
          }
            
             
          });
      },
      uploadFileInit() {
          const TOKEN = localStorage.getItem('token');
          axios.get('http://localhost:8000/folders/folder-create-list' , {
          headers: {
              'Authorization': `Bearer ${TOKEN}`,
            },
          })
        .then((response) => {
          const data = response.data
          this.changeUploadPaths(data)
          
          
           
        })
        .catch((error) => console.log(error))
      },
      changeUploadPaths(data) {
        this.upload_paths = []
        for(let i = 0; i < data.length; i++) {
          let path = {
            id: data[i].id,
            path: data[i].full_path
          }
          
          this.upload_paths.push(path)
        }
        this.boolUploadDialog = true
      },
      getMoveFilePaths(details){
        const TOKEN = localStorage.getItem('token');
          axios.get('http://localhost:8000/folders/folder-create-list', {
          headers: {
              'Authorization': `Bearer ${TOKEN}`,
            },
          })
        .then((response) => {
          const data = response.data
          this.changeMoveFilePaths(data, details["parent_dir_id"])
          
          
           
        })
        .catch((error) => console.log(error))
      },
      changeMoveFilePaths(data, id) {
        this.move_file_paths = []
        for(let i = 0; i < data.length; i++) {
          let path = {
            id: data[i].id,
            path: data[i].full_path
          }
          if (path.id === id) {
            continue
          }
          this.move_file_paths.push(path)
        }
        this.boolMoveFileDialog = true
      },
      moveFile(){
        const destinationID = this.destinationID_moveFile
        const file_id = this.moveFileID
        const TOKEN = localStorage.getItem('token')

        if (destinationID== 0) {
          this.boolMoveFileDialog = false
          this.moveFolderText = 'Please select a directory'
          this.boolSnackbarMove= true
          return
        }
        
        
        axios.patch(`http://localhost:8000/files/move?file_id=${file_id}&folder_id=${destinationID}`,
          {

          },
          {
            headers: {
              'Authorization': `Bearer ${TOKEN}`,
            },
          })
          .then((response) => {
            if(response.status === 200 && response.data === file_id){
              let index = -1 
              for(let i = 0; i < this.files.length; i++){
              if(this.files[i]["details"]["id"] === file_id) {
                index = i
                break;
              }
              }
              this.files.splice(index,1)
            }
            this.destinationID_moveFile= 0
            this.moveFileID = 0
            this.move_file_paths = []
            this.boolMoveFileDialog = false 
          })
          .catch((error) => {
            //ui for conflicts
            if(error.response.status === 404) {
              this.errorText = 'Not Found.'
              this.errorSnack = true
          } else if (error.response.status === 409){
            this.boolMoveFileDialog = false
            this.moveFolderText = 'The file cannot be moved as another file with same name exists in that directory'
            this.boolSnackbarMove= true

          } else{
              this.errorText = 'An error occured while processing your request.'
              this.errorSnack = true
          }
            
          });
        
      },
      trashFiles(details) {
        const TOKEN = localStorage.getItem('token')
          axios.patch(`http://localhost:8000/files/inactive?file_id=${details.id}`,
            {

            },
            {
              headers: {
                'Authorization': `Bearer ${TOKEN}`,
              },
            })
            .then((response) => {
              if(response.status === 200 && response.data === details.id){
               let index = -1 
               for(let i = 0; i < this.files.length; i++){
                if(this.files[i]["details"]["id"] === details.id) {
                  index = i
                  break;
                }
               }
               this.files.splice(index,1) 
              }

            })
            .catch((error) => {
              if( error.response.status === 404) {
              this.errorText = 'The file does not exist.'
              this.errorSnack = true
          } else {
              this.errorText = 'An error occured while processing your request.'
              this.errorSnack = true
          }
            });
      },
      changeFileScope(details){
        
        let new_scope = ''
        if (details.scope_type === 'public') {
          new_scope = 'private'
        } else if (details.scope_type === 'private') {
          new_scope = 'public'
        }
        const TOKEN = localStorage.getItem('token')
        axios.patch(`http://localhost:8000/files/scope?file_id=${details.id}&scope=${new_scope}`,
            {

            },
            {
            headers: {
            'Authorization': `Bearer ${TOKEN}`,
            },
          })
          .then((response) => {
            if(response.status === 200 && response.data === details.id) {
              for(let i = 0; i < this.files.length; i++){
                if(this.files[i]["details"]["id"] === details.id) {
                this.files[i]["details"]["scope_type"] = new_scope
                break;
              }
          }
            }
          })
          .catch((error) => {
              if( error.response.status === 404) {
              this.errorText = 'The file does not exist.'
              this.errorSnack = true
          } else {
              this.errorText = 'An error occured while processing your request.'
              this.errorSnack = true
          }
            });

      },
      
      displayFiles(data) {
        this.files  = []
        for (let i = 0; i < data.length; i++) {
          let file = {
          actionIcon: 'mdi-clock-outline',
          uploaded_on: 'Uploaded ' + new Date(data[i]["uploaded_on"]).toLocaleString(),
          color: '#91e1fb',
          icon: 'mdi-file',
          value: data[i]["name"],
          details : {
            id : data[i]["id"],
            parent_dir_id : data[i]["parent_directory_id"],
            full_path : data[i]["full_path"],
            scope_type : data[i]["scope_type"],
            is_starred: data[i]["is_starred"],
            size_in_gb: data[i]["size_in_gb"]
          }
          
          }
          this.files.push(file)
          
        }

      },
      


    },
    mounted() {
      const TOKEN = localStorage.getItem('token')
      
      axios.get( 'http://localhost:8000/files/starred', {
        headers: {
          'Authorization': `Bearer ${TOKEN}`,
        },
      })
      .then((response) => {
        const data = response.data;
        this.displayFiles(data) 
        
        
      })
      .catch((error) => console.log(error))

      }
      
    
  }
</script>
