package models

import (
	"fmt"
	"strings"
)

type Resource struct {
	CPUs          int    `yaml:"cpus,omitempty"`
	Memory        uint64 `yaml:"memory_mib,omitempty"`
	GPUs          []GPU  `yaml:"gpus,omitempty"`
	Interruptible bool   `yaml:"interruptible,omitempty"`
	ShmSize       int64  `yaml:"shm_size_mib,omitempty"`
	Local         bool   `json:"local"`
}

type Job struct {
	Apps         []App             `yaml:"apps"`
	Artifacts    []Artifact        `yaml:"artifacts"`
	Commands     []string          `yaml:"commands"`
	Environment  map[string]string `yaml:"env"`
	HostName     string            `yaml:"host_name"`
	Image        string            `yaml:"image_name"`
	JobID        string            `yaml:"job_id"`
	MasterJobID  string            `yaml:"master_job_id"`
	PortCount    int               `yaml:"port_count"`
	Ports        []string          `yaml:"ports"`
	Deps         []Dep             `yaml:"deps"`
	ProviderName string            `yaml:"provider_name"`

	RepoHostName       string `yaml:"repo_host_name"`
	RepoPort           int    `yaml:"repo_port,omitempty"`
	RepoBranch         string `yaml:"repo_branch"`
	RepoDiff           string `yaml:"repo_diff"`
	RepoHash           string `yaml:"repo_hash"`
	RepoName           string `yaml:"repo_name"`
	RepoUserName       string `yaml:"repo_user_name"`
	LocalRepoUserName  string `yaml:"local_repo_user_name,omitempty"`
	LocalRepoUserEmail string `yaml:"local_repo_user_email,omitempty"`

	RequestID    string       `yaml:"request_id"`
	Requirements Requirements `yaml:"requirements"`
	RunName      string       `yaml:"run_name"`
	RunnerID     string       `yaml:"runner_id"`
	Status       string       `yaml:"status"`
	SubmittedAt  uint64       `yaml:"submitted_at"`
	TagName      string       `yaml:"tag_name"`
	//Variables    map[string]interface{} `yaml:"variables"`
	WorkflowName string `yaml:"workflow_name"`
	WorkingDir   string `yaml:"working_dir"`
}

type Dep struct {
	RepoHostName string `yaml:"repo_host_name,omitempty"`
	RepoPort     int    `yaml:"repo_port,omitempty"`
	RepoUserName string `yaml:"repo_user_name,omitempty"`
	RepoName     string `yaml:"repo_name,omitempty"`
	RunName      string `yaml:"run_name,omitempty"`
	Mount        bool   `yaml:"mount,omitempty"`
}

type Artifact struct {
	Path  string `yaml:"path,omitempty"`
	Mount bool   `yaml:"mount,omitempty"`
}

type App struct {
	Name           string            `yaml:"app_name"`
	PortIdx        int               `yaml:"port_index"`
	UrlPath        string            `yaml:"url_path"`
	UrlQueryParams map[string]string `yaml:"url_query_params"`
}

type Requirements struct {
	GPUs          GPU   `yaml:"gpus,omitempty"`
	CPUs          int   `yaml:"cpus,omitempty"`
	Memory        int   `yaml:"memory_mib,omitempty"`
	Interruptible bool  `yaml:"interruptible,omitempty"`
	ShmSize       int64 `yaml:"shm_size_mib,omitempty"`
	Local         bool  `json:"local"`
}

type GPU struct {
	Count     int    `yaml:"count,omitempty"`
	Name      string `yaml:"name,omitempty"`
	MemoryMiB int    `yaml:"memory_mib,omitempty"`
}

type State struct {
	Job       *Job     `yaml:"job"`
	RequestID string   `yaml:"request_id"`
	Resources Resource `yaml:"resources"`
	RunnerID  string   `yaml:"runner_id"`
}

type GitCredentials struct {
	Protocol   string  `json:"protocol"`
	OAuthToken *string `json:"oauth_token,omitempty"`
	PrivateKey *string `json:"private_key,omitempty"`
	Passphrase *string `json:"passphrase,omitempty"`
}

type RepoData struct {
	RepoHost string
	RepoUserName string
	RepoName string
}

func (j *Job) RepoHostNameWithPort() string {
	if j.RepoPort == 0 {
		return j.RepoHostName
	}
	return fmt.Sprintf("%s:%d", j.RepoHostName, j.RepoPort)
}

func (d *Dep) RepoHostNameWithPort() string {
	if d.RepoPort == 0 {
		return d.RepoHostName
	}
	return fmt.Sprintf("%s:%d", d.RepoHostName, d.RepoPort)
}

func (rd *RepoData) RepoDataPath(sep string) string {
	return strings.Join([]string{rd.RepoHost, rd.RepoUserName, rd.RepoName}, sep)
}
