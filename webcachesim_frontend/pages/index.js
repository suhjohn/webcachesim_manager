import { useState } from "react";
import Button from "@material-ui/core/Button";
import { makeStyles } from "@material-ui/core/styles";
import Page from "../components/page";
import axios from "../axios";
import { useRouter } from "next/router";

const useStyles = makeStyles((theme) => ({
  page: {
    height: "100%"
  },
  taskList: {
    boxSizing: "border-box",
    "& > :not(:last-child)": {
      paddingBottom: "16px"
    }
  },
  taskItem: {
    display: "flex",
    flexWrap: "wrap",
    boxSizing: "border-box",
    "& > :not(:last-child)": {
      paddingRight: "16px"
    }
  }
}));

function TaskItem({ task, taskIndex }) {
  const classes = useStyles();
  const entries = Object.entries(task).map((entry, index) => {
    return (
      <p key={index}>
        {entry[0]}: {entry[1]}
      </p>
    );
  });
  return (
    <li className={classes.taskItem}>
      {taskIndex}: {entries}
    </li>
  );
}

function IndexPage() {
  const classes = useStyles();
  const router = useRouter();

  return (
    <Page>
      <div className={classes.page}></div>
    </Page>
  );
}

export default IndexPage;
