import { getAccounts } from "../../hooks/CuentasHooks";
import { useState,useEffect } from "react";
function CuentasContent(){
    const [Cuentas,setCuentas]= useState([]);
    useEffect(() => {
    const fetchAccounts = async () => {
      const data = await getAccounts(cliente_id, token);
      setCuentas(data);
    };

    fetchAccounts();
  }, [cliente_id, token]); 
    return(
        <div> Hola wey</div>
    );
}

export default CuentasContent;