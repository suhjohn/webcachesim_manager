import React from "react";
import clsx from "clsx";
import { makeStyles } from "@material-ui/core/styles";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import List from "@material-ui/core/List";
import Typography from "@material-ui/core/Typography";
import ListItem from "@material-ui/core/ListItem";
import { Icon } from "@material-ui/core";
import ListItemText from "@material-ui/core/ListItemText";
import AddIcon from "@material-ui/icons/Add";
import FormatListBulletedIcon from "@material-ui/icons/FormatListBulleted";
import HomeIcon from "@material-ui/icons/Home";
import Link from "next/link";
import { useRouter } from "next/router";
import { grey, blue } from "@ant-design/colors";

const drawerWidth = 240;

const useStyles = makeStyles((theme) => ({
  listItemRoot: {
    padding: 0,
    border: 0
  },
  listIcon: {
    width: "auto",
    padding: "0 24px"
  },
  listItemLink: {
    width: "100%",
    height: "52px",
    paddingLeft: "24px",
    display: "flex",
    alignItems: "center"
  },
  listItemUnselected: {
    "&:hover": {
      color: `${blue[6]}`,
      backgroundColor: "transparent"
    }
  },
  listItemSelected: {
    backgroundColor: `${blue[0]}`,
    color: `${blue[6]}`,
    borderRight: `1px solid ${blue[6]}`,
    "&:hover": {
      backgroundColor: `${blue[0]}`
    }
  },
  sideNavigation: {
    position: "sticky",
    left: 0,
    top: "62px",
    height: "calc(100vh - 62px)",
    borderRight: `1px solid #f5f5f5`
  },
  appBar: {
    zIndex: theme.zIndex.drawer + 1,
    height: "62px",
    backgroundColor: "white",
    color: "#000000",
    boxShadow: "none",
    borderBottom: `1px solid #f5f5f5`
  },
  drawerSide: {
    width: drawerWidth,
    flexShrink: 0
  },
  drawerPaper: {
    width: drawerWidth
  }
}));

export function TopNavigation() {
  const classes = useStyles();

  return (
    <AppBar position="sticky" className={classes.appBar}>
      <Toolbar>
        <Typography variant="h6" noWrap>
          Webcachesim Web Controller
        </Typography>
      </Toolbar>
    </AppBar>
  );
}

export function SideNavigation() {
  const classes = useStyles();
  const router = useRouter();
  const pages = [
    ["Home", "/", <HomeIcon />],
    ["Create", "/create", <AddIcon />],
    ["Remote Hosts", "/remote-hosts", <AddIcon />],
    ["List", "/list", <FormatListBulletedIcon />]
  ];
  const linkStyleCls = (link) => {
    return clsx({
      [classes.listItemLink]: true,
      [classes.listItemSelected]: link === router.pathname,
      [classes.listItemUnselected]: link !== router.pathname
    });
  };
  const listItemCls = (link) => {
    return clsx({
      [classes.listItemRoot]: true,
      [classes.listItemSelected]: link === router.pathname,
      [classes.listItemUnselected]: link !== router.pathname
    });
  };
  return (
    <div className={classes.sideNavigation}>
      <div className={classes.drawerSide}>
        <List>
          {pages.map(([text, link, icon], index) => (
            <ListItem button key={text} classes={{ root: listItemCls(link) }}>
              <Link href={link}>
                <a className={linkStyleCls(link)}>{text}</a>
              </Link>
            </ListItem>
          ))}
        </List>
      </div>
    </div>
  );
}
