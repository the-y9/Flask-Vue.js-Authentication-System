export default {
    template: `
        <div class="member-page">
            <div class="member-container">
                <h1 class="member-title">Welcome member {{ username }}</h1>
                <p class="member-text">This is the member page</p>
            </div>
        </div>`,
    
    data() {
        return {
            role: localStorage.getItem('role'),
            is_login: !!localStorage.getItem('auth-token'),
            username: localStorage.getItem('username'),
        };
    }

}