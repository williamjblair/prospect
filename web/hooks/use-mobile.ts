import * as React from "react";
export function useIsMobile() {
  const [m, setM] = React.useState(false);
  React.useEffect(() => {
    const q = window.matchMedia("(max-width: 768px)");
    const on = () => setM(q.matches); on(); q.addEventListener("change", on);
    return () => q.removeEventListener("change", on);
  }, []);
  return m;
}
