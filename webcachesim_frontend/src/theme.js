import { createMuiTheme } from "@material-ui/core/styles";
import { red } from "@material-ui/core/colors";
import { blue } from "@ant-design/colors";

// Create a theme instance.
const theme = createMuiTheme({
  typography: {
    fontFamily: [
      "Avenir",
      "-apple-system",
      "BlinkMacSystemFont",
      "Segoe UI",
      "PingFang SC",
      "Hiragino Sans GB",
      "Microsoft YaHei",
      "Helvetica Neue",
      "Apple Color Emoji",
      "Segoe UI Emoji",
      "Segoe UI Symbol",
      "sans-serif"
    ].join(","),
    h1: {
      fontSize: "30px",
      fontWeight: 500,
      marginTop: "8px",
      marginBottom: "20px",
      color: "#0d1a26",
      lineHeight: "38px"
    }
  },
  palette: {
    primary: {
      main: blue[5]
    },
    error: {
      main: red.A400
    },
    background: {
      default: "#fff"
    }
  }
});

export default theme;
