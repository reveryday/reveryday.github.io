import { createRoot } from "react-dom/client";
import CodeImageTool from "./CodeImageTool";

const root = document.getElementById("codeimage-root");
if (root) createRoot(root).render(<CodeImageTool />);
