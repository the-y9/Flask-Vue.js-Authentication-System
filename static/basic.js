import home from './components/home.js'
import login from './components/login.js'
import register from './components/register.js'
import Not_found_page from './components/Not_found_page.js'
import coach from './components/coach.js'
import member from './components/member.js'

export default [
    { path:'/' , component : home , name:'Home'},
    { path:'/login', component: login , name:'Login'},
    { path:'/404_page' , component: Not_found_page , name:'404_page'},
    { path:'/register', component: register, name:'Register'},
    { path:'/coach', component: coach, name:'Coach', meta: { requiresAuth: true, role: 'coach' } },
    { path:'/member', component: member, name:'Member', meta: { requiresAuth: true, role: 'member' } },
]