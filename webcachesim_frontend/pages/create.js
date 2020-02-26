import { useState } from "react";
import Button from "@material-ui/core/Button";
import { makeStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
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

function CreatePage({ tasks }) {
  const classes = useStyles();
  const router = useRouter();
  const onCreateClick = async () => {
    await axios.post("tasks/", {
      tasks: tasks
    });
    router.push("/list?status=created");
  };

  return (
    <Page>
      <div className={classes.page}>
        <Typography variant="h1">Create Tasks</Typography>
        <Button variant="contained" color="primary" onClick={onCreateClick}>
          Create Tasks
        </Button>
        <ul className={classes.taskList}>
          {tasks.map((task, index) => {
            return <TaskItem key={index} task={task} taskIndex={index} />;
          })}
        </ul>
      </div>
    </Page>
  );
}

CreatePage.getInitialProps = async (ctx) => {
  const resp = await axios.get("tasks/config/");
  return { tasks: resp.data.tasks };
};

export default CreatePage;
