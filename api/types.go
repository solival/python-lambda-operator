// +groupName=example.com
package v1

import (
	v1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// PythonLambda
// +k8s:deepcopy-gen:interfaces=k8s.io/apimachinery/pkg/runtime.Object
// +kubebuilder:subresource:status
// +kubebuilder:resource:path=pythonlambdas,scope=Namespaced
type PythonLambda struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata"`

	Spec   PythonLambdaSpec   `json:"spec"`
	Status PythonLambdaStatus `json:"status,omitempty"`
}

type PythonLambdaSpec struct {
	code     string `json:"code"`
	replicas int    `json:"replicas"`
	host     string `json:"host"`
}

type PythonLambdaStatus struct {
	conditions         []v1.PodCondition `json:"conditions,omitempty"`
	observedGeneration int               `json:"observedGeneration,omitempty"`
	readyReplicas      int               `json:"readyReplicas,omitempty"`
	replicas           int               `json:"replicas,omitempty"`
}
