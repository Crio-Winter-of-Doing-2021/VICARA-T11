/* eslint-disable */
<template>
    <div id="app">
    <v-app>
        <v-row justify="center">

      <div class="text-center ma-2">
      <v-snackbar
        v-model="registerSnack"
      >
        You have been sucessfully registered. Please login.
  
        <template v-slot:action="{ attrs }">
          <v-btn
            color="pink"
            text
            v-bind="attrs"
            @click="registerSnack= false"
          >
            Close
          </v-btn>
        </template>
      </v-snackbar>
    </div>
     </v-row>
        <v-dialog v-model="dialog" persistent max-width="600px" min-width="360px">
            <div>
                <v-tabs v-model="tab" show-arrows background-color="black accent-4" icons-and-text dark grow>
                    <v-tabs-slider color="purple darken-4"></v-tabs-slider>
                    <v-tab v-for="i in tabs" :key="i.key">
                        <v-icon large>{{ i.icon }}</v-icon>
                        <div class="caption py-1">{{ i.name }}</div>
                    </v-tab>
                    <v-tab-item>
                        <v-card class="px-4">
                            <v-card-text>
                                <v-form ref="loginForm" v-model="valid" lazy-validation>
                                    <v-row>
                                        <v-col cols="12">
                                            <v-text-field v-model="loginEmail" :rules="loginEmailRules" label="E-mail" required></v-text-field>
                                        </v-col>
                                        <v-col cols="12">
                                            <v-text-field v-model="loginPassword" :append-icon="show1?'mdi-eye':'mdi-eye-off'" :rules="[rules.required, rules.min]" :type="show1 ? 'text' : 'password'" name="input-10-1" label="Password" hint="At least 8 characters" counter @click:append="show1 = !show1"></v-text-field>
                                        </v-col>
                                        <v-col class="d-flex" cols="12" sm="6" xsm="12">
                                        </v-col>
                                        <v-spacer></v-spacer>
                                        <v-col class="d-flex" cols="12" sm="3" xsm="12" align-end>
                                            <v-btn x-large block :disabled="!valid" color="success" @click="validate"> Login </v-btn>
                                        </v-col>
                                    </v-row>
                                </v-form>
                            </v-card-text>
                        </v-card>
                    </v-tab-item>
                    <v-tab-item>
                        <v-card class="px-4">
                            <v-card-text>
                                <v-form ref="registerForm" v-model="valid" lazy-validation>
                                    <v-row>
                                        <v-col cols="12">
                                            <v-text-field v-model="email" :rules="emailRules" label="E-mail" required></v-text-field>
                                        </v-col>
                                        <v-col cols="12">
                                            <v-text-field v-model="password" :append-icon="show1 ? 'mdi-eye' : 'mdi-eye-off'" :rules="[rules.required, rules.min]" :type="show1 ? 'text' : 'password'" name="input-10-1" label="Password" hint="At least 8 characters" counter @click:append="show1 = !show1"></v-text-field>
                                        </v-col>
                                        <v-col cols="12">
                                            <v-text-field block v-model="verify" :append-icon="show1 ? 'mdi-eye' : 'mdi-eye-off'" :rules="[rules.required, passwordMatch]" :type="show1 ? 'text' : 'password'" name="input-10-1" label="Confirm Password" counter @click:append="show1 = !show1"></v-text-field>
                                        </v-col>
                                        <v-spacer></v-spacer>
                                        <v-col class="d-flex ml-auto" cols="12" sm="3" xsm="12">
                                            <v-btn x-large block :disabled="!valid" color="success" @click="register">Register</v-btn>
                                        </v-col>
                                    </v-row>
                                </v-form>
                            </v-card-text>
                        </v-card>
                    </v-tab-item>
                </v-tabs>
            </div>
        </v-dialog>
    </v-app>
</div>
</template>

<script>
import axios from 'axios'
import router from '@/router/index.js'
    export default {
         computed: {
    passwordMatch() {
      return () => this.password === this.verify || "Password must match";
    }
  },
  methods: {
    register() {
        if (this.$refs.registerForm.validate()) {
            axios.post('http://localhost:8000/auth/register', {
                email: this.email,
                password: this.password,
            })
            .then((response) => {
                this.reset()
                if(response.status === 201) {
                    this.registerSnack = true
                }
            })
            .catch((error) => console.log(error));
        }
    },
    validate() {
      if (this.$refs.loginForm.validate()) {
        // submit form to server/API here...
        
      const formData = new FormData();
      formData.set('username', this.loginEmail);
      formData.set('password', this.loginPassword);
      console.log(formData)  
      axios.post('http://localhost:8000/auth/jwt/login',
      formData,
      {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
      },
    )
    .then((response) =>  {

      localStorage.setItem('token', response.data.access_token)
      this.$store.commit('updateToken', response.data.access_token)

      router.push('/')
    })
    .catch((error) => console.log(error));
        //forgot_pass ui
      }
    },
    reset() {
      this.$refs.registerForm.reset();
    },
    resetValidation() {
      this.$refs.form.resetValidation();
    },
  
  },
  data: () => ({
    registerSnack: false,
    dialog: true,
    tab: 0,
    tabs: [
        {key:0, name:"Login", icon:"mdi-account"},
        {key:1, name:"Register", icon:"mdi-account-outline"}
    ],
    valid: true,
    timeout: 2000,
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    verify: "",
    loginPassword: "",
    loginEmail: "",
    loginEmailRules: [
      v => !!v || "Required",
      v => /.+@.+\..+/.test(v) || "E-mail must be valid"
    ],
    emailRules: [
      v => !!v || "Required",
      v => /.+@.+\..+/.test(v) || "E-mail must be valid"
    ],

    show1: false,
    rules: {
      required: value => !!value || "Required.",
      min: v => (v && v.length >= 8) || "Min 8 characters"
    }
    })
    }
</script>

<style lang="scss" scoped>

</style>