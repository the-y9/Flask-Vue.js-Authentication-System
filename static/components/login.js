
export default {
    template: `
      <div class="login-page">
        <div class="login-container">

          <img :src="image" alt="Profile Picture" class="profile-pic" />
          <div class="error-message text-danger text-center">{{ error }}</div>  
          <h1 class="login-title">Please Login</h1>
          
          <div class="form-group">
            <label for="username" class="form-label">Username</label> 
            <input type="text" class="form-control" id="username" v-model="cred.username" placeholder="Enter your username">
          </div>
          
          <div class="form-group">
            <label for="user_password" class="form-label">Password</label>
            <input type="password" class="form-control" id="user_password" v-model="cred.password" placeholder="Enter your password">
          </div>
          
          <button class="btn btn-primary button-1" @click="login">Login</button>
          
          <p class="register-link text-center">
            Don't have an account? <router-link to="/register">Register</router-link>
          </p>
        </div>
      </div>`,
      
    data() {
      return {
        cred: {
          username: null,
          password: null,
        },
        error: null,
        image : "static/images/user.png",
      }
    },
    
    methods: {
      async login() {
        try {
          const res = await fetch('/user-login', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(this.cred),
          })
          const data = await res.json()
          if (res.ok) {
            localStorage.setItem('auth-token', data.token)
            localStorage.setItem('role', data.role)
            localStorage.setItem('username', data.username)
            localStorage.setItem('user_id', data.id)
            
            if (data.role == "member"){
            this.$router.push({ path: '/member' })
            }
            else if (data.role == "root" || data.role == "coach" || data.role == "ta" ){
                this.$router.push({ path: '/coach' })
            }
          } else {
            this.error = data.message
          }
          // console.log(error)
        } catch (error) {
          console.log("ERROR:" ,error)
        }
      }
    },
    mounted() {
      const message = this.$route.query.message;
      if (message) {
        console.log("Message is :=", message);
        this.error = message;
      }
    }    
  }
  