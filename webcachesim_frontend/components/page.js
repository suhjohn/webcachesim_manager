import { TopNavigation, SideNavigation } from "./navigation";
import { makeStyles } from "@material-ui/core/styles";
const useStyles = makeStyles((theme) => ({
  page: { display: "flex", width: "100vw" },
  body: {
    flex: 1,
    padding: "24px"
  },
  bodyBody: {}
}));

function Page({ children }) {
  const classes = useStyles();
  return (
    <div>
      <TopNavigation />
      <div className={classes.page}>
        <SideNavigation />
        <div className={classes.body}>{children}</div>
      </div>
    </div>
  );
}

export default Page;
