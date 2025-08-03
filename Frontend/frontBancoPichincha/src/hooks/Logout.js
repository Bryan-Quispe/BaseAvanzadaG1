function Logout(){
    localStorage.clear();
    window.location.reload();
}

export {Logout};