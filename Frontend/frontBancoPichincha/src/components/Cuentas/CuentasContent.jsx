
import { useState,useEffect } from "react";
import AccountSlider from './CuentaCarusel';
function CuentasContent(){

    return(
         <div className="p-6 bg-gray-50 min-h-screen">
      <h2 className="text-2xl font-bold text-blue-900 mb-4">
        Mis Cuentas
      </h2>

        <AccountSlider />
      
    </div>
    );
}

export default CuentasContent;