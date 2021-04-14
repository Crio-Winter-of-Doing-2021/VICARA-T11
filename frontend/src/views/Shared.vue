<template>
  <v-container
    id="dashboard-view"
    fluid
    tag="section"
  >

    <view-intro
      :heading="folders.length === 0 && files.length === 0 ? 'No files or folders have been shared': ''"
    />
    

    <view-intro
      :heading="folders.length === 0 ? '' : 'Shared Folders'"
    />
    <v-row>
      
      <v-col
        v-for="({ actionIcon, created_on, details, ...attrs }, i) in folders"
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
              {{ created_on }}
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
                  v-for="({title}, i) in folder_utils"
                  :key="i"
                  @click="log(title, details)"
                >
                
                  <v-list-item-title v-if="details.scope_type === 'private' && title === 'Make'">Make Public</v-list-item-title>
                  <v-list-item-title v-else-if="details.scope_type === 'public' && title === 'Make'">Make Private</v-list-item-title>
                  <v-list-item-title v-else>{{ title }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
            </v-col>
          </template>
        </material-stat-card>
      </v-col>
    </v-row>

    <br>
    <br>
    <br>
    <br>

    <view-intro
      :heading="files.length === 0 ? '' : 'Shared Files'"
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
      files: [],
      results : [],
      folders: [
      ],
      tabs: 0,
      folder_utils: [
      { title: 'Make', },

    ],
      file_utils: [
      { title: 'Make', },
      
    ],
    }), 
    methods:{
      file_log(string, details) {
        if(string === 'Make') {
          this.changeFileScope(details)
        }
    
  
      },
      log(string, details) {
        if (string === 'Make') {
          this.changeScope(details)
        } 

    
  
      },
            changeScope(details) {
        let new_scope = ''
          if (details.scope_type === 'public') {
            new_scope = 'private'
          } else if (details.scope_type === 'private') {
            new_scope = 'public'
          }
          const TOKEN = localStorage.getItem('token')
          axios.patch(`http://localhost:8000/folders/scope?folder_id=${details.id}&scope=${new_scope}`,
            {

            },
            {
            headers: {
            'Authorization': `Bearer ${TOKEN}`,
            },
          })
          .then((response) => {
            if(response.status === 200 && response.data === details.id) {
              let index = -1
              for(let i = 0; i < this.folders.length; i++){
                if(this.folders[i]["details"]["id"] === details.id) {
                this.folders[i]["details"]["scope_type"] = new_scope
                index = i
                break;
              }
            }
             this.folders.splice(index,1)
            }
          })
          .catch((error) => {
              if( error.response.status === 404) {
              this.errorText = 'The folder does not exist.'
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
              let index = -1
              for(let i = 0; i < this.files.length; i++){
                if(this.files[i]["details"]["id"] === details.id) {
                this.files[i]["details"]["scope_type"] = new_scope
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
            size_in_gb: data[i]["size_in_gb"]
          }
          
          }
          this.files.push(file)
          
        }

      },
      displayFolders(data) {
        this.folders  = []
        for (let i = 0; i < data.length; i++) {
          let folder = {
          actionIcon: 'mdi-clock-outline',
          created_on: 'Created ' + new Date(data[i]["created_on"]).toLocaleString(),
          color: '#FD9A13',
          icon: 'mdi-folder-open',
          value: data[i]["name"],
          details : {
            id : data[i]["id"],
            full_path : data[i]["full_path"],
            scope_type : data[i]["scope_type"]

          }
          
          }
          this.folders.push(folder)
          
        }

      },

    },
    mounted() {
      const TOKEN = localStorage.getItem('token')
      axios.get( 'http://localhost:8000/folders/public', {
        headers: {
          'Authorization': `Bearer ${TOKEN}`,
        },
      })
      .then((response) => {
        const data = response.data;
        this.displayFolders(data) 
        
        
      })
      .catch((error) => console.log(error))

      axios.get( 'http://localhost:8000/files/public', {
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
